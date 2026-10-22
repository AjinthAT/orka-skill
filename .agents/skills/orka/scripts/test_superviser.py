"""Tests sur registres temporaires et agents simules ; aucun lancement de modele."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from preparer_agent import SKILL_ROOT
from superviser import Superviseur


class SupervisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.racine = Path(self.tmp.name)
        self.base = self.racine / "registre.sqlite"
        self.temps = 1000
        Superviseur.initialiser(self.base, self.racine, 1)
        self.sup = Superviseur(self.base, horloge=lambda: self.temps)
        self.addCleanup(lambda: self.sup.fermer())
        self.exemple = json.loads((SKILL_ROOT / "assets" / "mandat-exemple.json").read_text())

    def ajouter(self, tache="T1", mission="test", fichier=None, dependances=(), maximum=2):
        mandat = deepcopy(self.exemple)
        mandat.update(mission_id=mission, tache_id=tache, sortie=fichier or (tache + ".md"))
        self.sup.ajouter(mandat, mandat["sortie"], dependances, maximum)
        return mandat

    def observations(self, etat="satisfait"):
        return {f"C-{i:02d}": {"etat": etat, "preuve": "Constat de test local, donnees simulees"}
                for i in range(1, len(self.exemple["criteres"]) + 1)}

    def produire(self, tache="T1", mission="test"):
        execution = self.sup.reserver(mission, tache)
        identifiant = execution["execution_id"]
        self.sup.attacher(identifiant, "agent-simule-" + identifiant)
        fichier = Path(self.sup.tache(mission, tache)["fichier"])
        fichier.write_text("Resultat simule pour le test", encoding="utf-8")
        self.sup.soumettre(identifiant, self.observations())
        return identifiant

    def terminer(self, tache="T1"):
        identifiant = self.produire(tache)
        self.sup.liberer(identifiant, "Simulation : aucun agent externe n'a ete lance")
        self.sup.accepter("test", tache, "coordinateur")
        return identifiant

    def test_pipeline_persiste_apres_fermeture_et_nouvelle_session(self):
        self.ajouter()
        self.ajouter("T2", dependances=["T1"])
        with self.assertRaisesRegex(ValueError, "Dependances"):
            self.sup.reserver("test", "T2")
        self.terminer()
        self.sup.fermer()
        self.sup = Superviseur(self.base)
        self.assertEqual(self.sup.tache("test", "T1")["etat"], "terminee")
        requete = self.sup.reserver("test", "T2")
        self.assertEqual(requete["phase"], "reservee")
        self.assertIsNone(requete["requete"]["parametres_appliques"])
        self.assertTrue(any(e["type"] == "acceptation" for e in self.sup.journal()))

    def test_deux_connexions_ne_depassent_pas_la_capacite_globale(self):
        self.ajouter("T1", mission="premiere")
        self.ajouter("T2", mission="seconde")

        def reserver(mission, tache):
            connexion = Superviseur(self.base)
            try:
                return connexion.reserver(mission, tache)
            except ValueError as exc:
                return str(exc)
            finally:
                connexion.fermer()

        with ThreadPoolExecutor(max_workers=2) as pool:
            premier = pool.submit(reserver, "premiere", "T1")
            second = pool.submit(reserver, "seconde", "T2")
            resultats = [premier.result(), second.result()]
        self.assertEqual(sum(isinstance(r, dict) for r in resultats), 1)
        self.assertEqual(len(self.sup.etat()["actives"]), 1)

    def test_fichier_partage_reste_reserve_malgre_silence(self):
        self.sup.db.execute("UPDATE configuration SET capacite=2")
        self.sup.capacite = 2
        self.ajouter("T1", fichier="commun.md")
        self.ajouter("T2", fichier="sous/../commun.md")
        identifiant = self.sup.reserver("test", "T1")["execution_id"]
        self.temps += 400
        self.assertEqual(len(self.sup.alertes(300)), 1)
        with self.assertRaisesRegex(ValueError, "Fichier deja reserve"):
            self.sup.reserver("test", "T2")
        self.sup.liberer(identifiant, "Reservation jamais lancee, absence de redacteur confirmee")
        self.assertEqual(self.sup.reserver("test", "T2")["phase"], "reservee")

    def test_reprise_exige_liberation_et_borne_les_tentatives(self):
        self.ajouter()
        premiere = self.sup.reserver("test", "T1")
        identifiant = premiere["execution_id"]
        self.sup.liberer(identifiant, "Reservation non lancee")
        self.sup.reprendre("test", "T1", "Nouvelle tentative de test")
        seconde = self.sup.reserver("test", "T1")
        self.assertEqual(seconde["requete"]["tentative"], 2)
        self.assertNotEqual(premiere["requete"]["parametres_demandes"]["task_name"],
                            seconde["requete"]["parametres_demandes"]["task_name"])
        with self.assertRaisesRegex(ValueError, "liberee"):
            self.sup.battement(identifiant)
        self.sup.liberer(seconde["execution_id"], "Reservation non lancee")
        with self.assertRaisesRegex(ValueError, "Limite"):
            self.sup.reprendre("test", "T1", "Troisieme tentative interdite")

    def test_resultat_ne_libere_pas_implicitement_le_redacteur(self):
        self.ajouter()
        identifiant = self.produire()
        with self.assertRaisesRegex(ValueError, "redacteur actif"):
            self.sup.accepter("test", "T1", "coordinateur")
        with self.assertRaisesRegex(ValueError, "ancien redacteur"):
            self.sup.reprendre("test", "T1", "Correction prematuree")
        self.sup.liberer(identifiant, "Fin de l'agent simule confirmee")
        with self.assertRaisesRegex(ValueError, "responsable"):
            self.sup.accepter("test", "T1", "autre-role")
        self.sup.accepter("test", "T1", "coordinateur")

    def test_fichier_modifie_apres_soumission_est_refuse(self):
        self.ajouter()
        identifiant = self.produire()
        self.sup.liberer(identifiant, "Fin de l'agent simule")
        (self.racine / "T1.md").write_text("Autre version")
        with self.assertRaisesRegex(ValueError, "Version"):
            self.sup.accepter("test", "T1", "coordinateur")

    def test_dependance_acceptee_modifiee_bloque_son_aval(self):
        self.ajouter()
        self.ajouter("T2", dependances=["T1"])
        self.terminer()
        (self.racine / "T1.md").write_text("Modification apres acceptation")
        with self.assertRaisesRegex(ValueError, "Dependances"):
            self.sup.reserver("test", "T2")
        self.assertFalse(self.sup.etat()["taches"][1]["prete"])

    def test_criteres_incomplets_non_verifies_ou_sans_preuve_refuses(self):
        self.ajouter()
        identifiant = self.sup.reserver("test", "T1")["execution_id"]
        self.sup.attacher(identifiant, "agent-simule")
        (self.racine / "T1.md").write_text("Simulation")
        with self.assertRaisesRegex(ValueError, "exactement"):
            self.sup.soumettre(identifiant, {})
        observations = self.observations()
        observations["C-01"]["preuve"] = ""
        with self.assertRaises(ValueError):
            self.sup.soumettre(identifiant, observations)
        self.sup.soumettre(identifiant, self.observations("non_verifie"))
        self.sup.liberer(identifiant, "Fin de la simulation")
        with self.assertRaisesRegex(ValueError, "critere"):
            self.sup.accepter("test", "T1", "coordinateur")

    def test_transaction_annule_etat_et_journal_en_cas_dechec(self):
        self.ajouter()
        with patch.object(self.sup, "evenement", side_effect=RuntimeError("Panne simulee")):
            with self.assertRaises(RuntimeError):
                self.sup.reserver("test", "T1")
        self.assertEqual(self.sup.tache("test", "T1")["tentatives"], 0)
        self.assertEqual(self.sup.tache("test", "T1")["etat"], "a_faire")
        self.assertEqual(self.sup.etat()["actives"], [])

    def test_dependances_inconnues_ou_cycliques_refusees(self):
        with self.assertRaises(ValueError):
            self.ajouter("T1", dependances=["T1"])
        with self.assertRaises(ValueError):
            self.ajouter("T1", dependances=["future"])
        self.assertEqual(self.sup.etat()["taches"], [])

    def test_chemins_hors_racine_et_fichiers_du_registre_refuses(self):
        with self.assertRaises(ValueError):
            self.ajouter(fichier="../interdit.md")
        with self.assertRaises(ValueError):
            self.ajouter(fichier=str(self.base))

    def test_requete_est_figee_et_ne_recharge_pas_les_profils_a_la_reservation(self):
        self.ajouter()
        with patch("superviser.preparer", side_effect=AssertionError("Ne pas recompiler")):
            execution = self.sup.reserver("test", "T1")
        self.assertEqual(execution["requete"]["parametres_demandes"]["model"], "gpt-6-luna")
        self.assertEqual(len(execution["requete"]["criteres_attendus"]), len(self.exemple["criteres"]))

    def test_agent_ne_peut_pas_etre_rattache_a_deux_taches_actives(self):
        self.sup.db.execute("UPDATE configuration SET capacite=2")
        self.sup.capacite = 2
        self.ajouter()
        self.ajouter("T2")
        premiere = self.sup.reserver("test", "T1")["execution_id"]
        seconde = self.sup.reserver("test", "T2")["execution_id"]
        self.sup.attacher(premiere, "agent-simule-unique")
        with self.assertRaises(sqlite3.IntegrityError):
            self.sup.attacher(seconde, "agent-simule-unique")
        self.assertEqual(self.sup.execution(seconde)["phase"], "reservee")

    def test_reglages_observes_restent_declares_et_distincts_des_demandes(self):
        self.ajouter()
        identifiant = self.sup.reserver("test", "T1")["execution_id"]
        self.assertIsNone(self.sup.etat()["taches"][0]["parametres_appliques_declares"])
        self.sup.attacher(identifiant, "agent-simule", {"model": "modele-de-test", "reasoning_effort": "effort-de-test"})
        etat = self.sup.etat()["taches"][0]
        self.assertEqual(etat["modele_demande"], "gpt-6-luna")
        self.assertEqual(etat["parametres_appliques_declares"]["model"], "modele-de-test")

    def test_reprise_transmet_le_constat_sans_changer_les_reglages(self):
        self.ajouter()
        identifiant = self.produire()
        premiere = self.sup.requete(identifiant)["requete"]
        self.sup.liberer(identifiant, "Fin de l'agent simule")
        self.sup.reprendre("test", "T1", "Revoir la seconde formulation")
        seconde = self.sup.reserver("test", "T1")["requete"]
        self.assertIn("Revoir la seconde formulation", seconde["parametres_demandes"]["message"])
        self.assertEqual(seconde["contexte_reprise"]["observations_precedentes"], self.observations())
        self.assertEqual(premiere["parametres_demandes"]["model"], seconde["parametres_demandes"]["model"])
        self.assertNotEqual(premiere["empreinte_prompt"], seconde["empreinte_prompt"])

    def test_cli_recupere_une_reservation_apres_perte_de_reponse(self):
        self.ajouter()
        identifiant = self.sup.reserver("test", "T1")["execution_id"]
        commande = [sys.executable, "-B", str(SKILL_ROOT / "scripts" / "superviser.py"),
                    "--base", str(self.base), "requete", "--execution", identifiant]
        resultat = json.loads(subprocess.run(commande, capture_output=True, text=True, check=True).stdout)
        self.assertEqual(resultat["execution_id"], identifiant)
        self.assertEqual(resultat["phase"], "reservee")
        self.assertIsNone(resultat["agent"])
        self.assertEqual(len(self.sup.etat()["actives"]), 1)

    def test_cli_initialisation_et_lecture_sans_creation_implicite(self):
        commande = [sys.executable, "-B", str(SKILL_ROOT / "scripts" / "superviser.py"),
                    "--base", str(self.racine / "absente.sqlite"), "etat"]
        refus = subprocess.run(commande, capture_output=True, text=True)
        self.assertEqual(refus.returncode, 2)
        self.assertFalse((self.racine / "absente.sqlite").exists())
        commande[4] = str(self.base)
        lecture = subprocess.run(commande, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(lecture.stdout)["capacite"], 1)
        # Une nouvelle initialisation ne doit jamais effacer le registre existant.
        with self.assertRaises(FileExistsError):
            Superviseur.initialiser(self.base, self.racine)


if __name__ == "__main__":
    unittest.main()
