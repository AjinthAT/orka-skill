"""Tests sur registres temporaires et agents simules ; aucun lancement de modele."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from preparer_agent import SKILL_ROOT
from superviser import Superviseur, empreinte_fichier


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
        self.exemple = json.loads((SKILL_ROOT / "assets" / "mandat-exemple.json").read_text(encoding="utf-8"))

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
        resultat = json.loads(subprocess.run(commande, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
        self.assertEqual(resultat["execution_id"], identifiant)
        self.assertEqual(resultat["phase"], "reservee")
        self.assertIsNone(resultat["agent"])
        self.assertEqual(len(self.sup.etat()["actives"]), 1)

    def test_cli_initialisation_et_lecture_sans_creation_implicite(self):
        commande = [sys.executable, "-B", str(SKILL_ROOT / "scripts" / "superviser.py"),
                    "--base", str(self.racine / "absente.sqlite"), "etat"]
        refus = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(refus.returncode, 2)
        self.assertFalse((self.racine / "absente.sqlite").exists())
        commande[4] = str(self.base)
        lecture = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(lecture.stdout)["capacite"], 1)
        # Une nouvelle initialisation ne doit jamais effacer le registre existant.
        with self.assertRaises(FileExistsError):
            Superviseur.initialiser(self.base, self.racine)

    def test_dependance_indirecte_invalide_bloque_trois_niveaux(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.ajouter("C", dependances=["B"])
        self.ajouter("D", dependances=["C"])
        for tache in ("A", "B", "C"):
            self.terminer(tache)
        (self.racine / "A.md").write_text("Entree modifiee", encoding="utf-8")
        for tache in ("A", "B", "C"):
            self.assertFalse(self.sup.reference_valide(self.sup.tache("test", tache)))
        self.assertEqual(self.sup.manquantes("test", "D"), ["C"])
        with self.assertRaisesRegex(ValueError, "Dependances"):
            self.sup.reserver("test", "D")
        etats = {t["id"]: t for t in self.sup.etat()["taches"]}
        self.assertEqual(etats["B"]["etat"], "terminee")
        self.assertEqual(etats["B"]["validite"], "a_reexaminer")
        self.assertEqual(etats["B"]["entrees_a_reexaminer"], ["A"])

    def test_version_entree_changee_meme_si_octets_identiques_refuse_acceptation(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        premiere = self.terminer("A")
        resultat = self.produire("B")
        self.sup.liberer(resultat, "Fin de la simulation")
        entrees = json.loads(self.sup.execution(resultat, active=False)["entrees"])
        self.assertEqual(entrees["A"]["execution_id"], premiere)
        self.sup.reexaminer("test", "A", "Nouvelle validation de la source", "coordinateur")
        self.sup.reprendre("test", "A", "Verifier de nouveau")
        seconde = self.terminer("A")
        self.assertNotEqual(premiere, seconde)
        self.assertEqual(self.sup.execution(premiere, False)["empreinte"], self.sup.execution(seconde, False)["empreinte"])
        with self.assertRaisesRegex(ValueError, "Version"):
            self.sup.accepter("test", "B", "coordinateur")
        self.assertEqual(json.loads(self.sup.execution(resultat, False)["entrees"]), entrees)

    def test_reexamen_conserve_historique_et_recalcule_seulement_apres_reprise(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.ajouter("C", dependances=["B"])
        self.terminer("A")
        ancienne = self.terminer("B")
        attendu = dict(self.sup.execution(ancienne, False))
        reexamen = self.sup.reexaminer("test", "B", "Verifier les conclusions", "coordinateur")
        self.assertEqual(reexamen["dependants_a_reexaminer"], ["C"])
        self.assertEqual(self.sup.tache("test", "B")["etat"], "a_reexaminer")
        with self.assertRaisesRegex(ValueError, "Dependances"):
            self.sup.reserver("test", "C")
        self.sup.reprendre("test", "B", "Corriger apres reexamen")
        nouvelle = self.terminer("B")
        self.assertEqual(self.sup.execution(nouvelle, False)["numero"], 2)
        self.assertEqual(dict(self.sup.execution(ancienne, False)), attendu)
        self.assertTrue(self.sup.reference_valide(self.sup.tache("test", "B")))
        self.assertEqual(self.sup.reserver("test", "C")["requete"]["entrees_verifiees"]["B"]["execution_id"], nouvelle)
        self.assertEqual(sum(e["type"] == "acceptation" for e in self.sup.journal()), 3)

    def test_reexamen_exige_motif_responsable_et_absence_de_redacteur(self):
        self.ajouter()
        self.terminer()
        for motif, validateur in (("", "coordinateur"), ("motif", "autre")):
            with self.assertRaises(ValueError):
                self.sup.reexaminer("test", "T1", motif, validateur)
        self.ajouter("autre", fichier="T1.md")
        self.sup.reserver("test", "autre")
        with self.assertRaisesRegex(ValueError, "redacteur"):
            self.sup.reexaminer("test", "T1", "Source revue", "coordinateur")
        self.assertEqual(self.sup.tache("test", "T1")["etat"], "terminee")

    def test_reexamen_ne_remet_pas_a_zero_les_limites(self):
        self.ajouter(maximum=1)
        self.terminer()
        self.sup.reexaminer("test", "T1", "Donnees perimees", "coordinateur")
        with self.assertRaisesRegex(ValueError, "Limite"):
            self.sup.reprendre("test", "T1", "Nouvel essai")
        self.assertEqual(self.sup.tache("test", "T1")["tentatives"], 1)
        self.assertEqual(self.sup.tache("test", "T1")["etat"], "a_reexaminer")

    def test_reexamen_transactionnel_et_detection_cycle_defensive(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.terminer("A")
        self.terminer("B")
        with patch.object(self.sup, "evenement", side_effect=RuntimeError("Panne simulee")):
            with self.assertRaises(RuntimeError):
                self.sup.reexaminer("test", "A", "Constat", "coordinateur")
        self.assertEqual(self.sup.tache("test", "A")["etat"], "terminee")
        # Une alteration directe de la base ne doit pas provoquer de recursion infinie.
        self.sup.db.execute("INSERT INTO dependances VALUES ('test','A','B')")
        self.assertFalse(self.sup.reference_valide(self.sup.tache("test", "B")))

    def ancienne_base(self):
        base = self.racine / "historique.sqlite"
        copie = sqlite3.connect(str(base))
        copie.executescript((Path(__file__).parent / "fixtures/registre-v1.sql").read_text(encoding="utf-8"))
        for table in ("configuration", "taches", "dependances", "tentatives", "evenements"):
            colonnes = [r[1] for r in copie.execute(f"PRAGMA table_info({table})")]
            lignes = self.sup.db.execute(f"SELECT {','.join(colonnes)} FROM {table}").fetchall()
            copie.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in colonnes)})", [tuple(r) for r in lignes])
        copie.execute("UPDATE configuration SET version=1")
        copie.commit()
        copie.close()
        return base

    def test_migration_explicite_sauvegarde_et_preservation_des_donnees_v1(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.ajouter("C", dependances=["B"])
        self.ajouter("D", dependances=["A"])
        self.terminer("A")
        self.terminer("B")
        active = self.sup.reserver("test", "D")["execution_id"]
        base = self.ancienne_base()
        contenu = base.read_bytes()
        with self.assertRaisesRegex(ValueError, "migrer"):
            Superviseur(base)
        self.assertEqual(base.read_bytes(), contenu)
        resultat = Superviseur.migrer(base)
        sauvegarde = Path(resultat["sauvegarde"])
        self.assertTrue(sauvegarde.is_file())
        with closing(sqlite3.connect(str(sauvegarde))) as avant, closing(sqlite3.connect(str(base))) as apres:
            self.assertEqual(avant.execute("SELECT version FROM configuration").fetchone()[0], 1)
            self.assertEqual(apres.execute("SELECT version FROM configuration").fetchone()[0], 2)
            for table in ("taches", "dependances", "tentatives", "evenements"):
                colonnes = [r[1] for r in avant.execute(f"PRAGMA table_info({table})")]
                filtre = " WHERE type<>'migration_v2'" if table == "evenements" else ""
                self.assertEqual(avant.execute(f"SELECT {','.join(colonnes)} FROM {table}").fetchall(),
                                 apres.execute(f"SELECT {','.join(colonnes)} FROM {table}{filtre}").fetchall())
        with self.subTest("utilisation apres migration"):
            sup = Superviseur(base)
            try:
                self.assertEqual(sup.execution(active)["phase"], "reservee")
                self.assertTrue(sup.reference_valide(sup.tache("test", "A")))
                self.assertFalse(sup.reference_valide(sup.tache("test", "B")))
                with self.assertRaisesRegex(ValueError, "Dependances"):
                    sup.reserver("test", "C")
                self.assertIsNone(sup.etat()["taches"][1]["entrees_utilisees"])
                sup.attacher(active, "agent-simule-apres-migration")
                (self.racine / "D.md").write_text("Resultat simule", encoding="utf-8")
                sup.soumettre(active, self.observations())
                sup.liberer(active, "Fin de la simulation")
                with self.assertRaisesRegex(ValueError, "Version"):
                    sup.accepter("test", "D", "coordinateur")
            finally:
                sup.fermer()
        self.assertEqual(Superviseur.migrer(base), {"etat": "registre_deja_v2", "sauvegarde": None})
        self.assertEqual(len(list(self.racine.glob("*.avant-v2-*.sqlite"))), 1)

    def test_migration_inclut_wal_et_annule_les_modifications_en_cas_dechec(self):
        self.ajouter()
        base = self.ancienne_base()
        wal = sqlite3.connect(str(base))
        try:
            wal.execute("PRAGMA journal_mode=WAL")
            wal.execute("INSERT INTO evenements(date,type,details) VALUES (1,'avant_migration','{}')")
            wal.commit()
            resultat = Superviseur.migrer(base)
            with closing(sqlite3.connect(resultat["sauvegarde"])) as copie:
                self.assertEqual(copie.execute("SELECT COUNT(*) FROM evenements WHERE type='avant_migration'").fetchone()[0], 1)
        finally:
            wal.close()
        base.unlink()
        base = self.ancienne_base()
        with closing(sqlite3.connect(str(base))) as connexion:
            connexion.execute("CREATE TRIGGER panne BEFORE UPDATE ON configuration BEGIN SELECT RAISE(ABORT,'panne simulee'); END")
            connexion.commit()
        with self.assertRaises(sqlite3.Error):
            Superviseur.migrer(base)
        with closing(sqlite3.connect(str(base))) as connexion:
            self.assertEqual(connexion.execute("SELECT version FROM configuration").fetchone()[0], 1)
            self.assertNotIn("entrees", [r[1] for r in connexion.execute("PRAGMA table_info(tentatives)")])

    def test_cli_reexamen_et_migration_absente_ne_cree_pas_de_base(self):
        self.ajouter()
        self.terminer()
        commande = [sys.executable, "-B", str(SKILL_ROOT / "scripts/superviser.py"), "--base", str(self.base)]
        resultat = subprocess.run(commande + ["reexaminer", "--mission", "test", "--tache", "T1",
                                  "--motif", "Revoir", "--validateur", "coordinateur"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        self.assertEqual(json.loads(resultat.stdout)["etat"], "a_reexaminer")
        absente = self.racine / "absente.sqlite"
        resultat = subprocess.run(commande[:4] + [str(absente), "migrer"], capture_output=True)
        self.assertEqual(resultat.returncode, 2)
        self.assertFalse(absente.exists())

    def test_ancienne_conclusion_reste_invalide_apres_revalidation_de_sa_source(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.ajouter("C", dependances=["B"])
        self.terminer("A")
        self.terminer("B")
        self.sup.reexaminer("test", "A", "Nouvelle source", "coordinateur")
        self.sup.reprendre("test", "A", "Verifier la source")
        self.terminer("A")
        self.assertTrue(self.sup.reference_valide(self.sup.tache("test", "A")))
        self.assertFalse(self.sup.reference_valide(self.sup.tache("test", "B")))
        with self.assertRaisesRegex(ValueError, "Dependances"):
            self.sup.reserver("test", "C")

    def test_cli_etat_utf8_sous_locale_ascii(self):
        self.ajouter(mission="été")
        environnement = dict(os.environ, LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0", PYTHONIOENCODING="ascii")
        resultat = subprocess.run([sys.executable, "-B", str(SKILL_ROOT / "scripts/superviser.py"),
                                  "--base", str(self.base), "etat"], env=environnement, capture_output=True)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        self.assertEqual(json.loads(resultat.stdout.decode("utf-8"))["taches"][0]["mission"], "été")

    def test_graphe_partage_ne_relit_pas_plusieurs_fois_chaque_reference(self):
        self.ajouter("A")
        self.ajouter("B", dependances=["A"])
        self.ajouter("C", dependances=["A"])
        self.ajouter("D", dependances=["B", "C"])
        for tache in ("A", "B", "C", "D"):
            self.terminer(tache)
        with patch("superviser.empreinte_fichier", wraps=empreinte_fichier) as calcul:
            self.assertTrue(self.sup.reference_valide(self.sup.tache("test", "D")))
            self.assertEqual(calcul.call_count, 4)


if __name__ == "__main__":
    unittest.main()
