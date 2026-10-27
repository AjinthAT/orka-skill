"""AUT-02A : vrais processus logiciels fixes, aucun modèle ni fournisseur."""

import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from tools.supervision_locale.controleur import Controleur, MISSION, Superviseur, creer, etat, suspendre
from tools.supervision_locale.processus import ProcessusFixes, TRAVAILLEUR
from tools.supervision_locale.stockage import ecrire, evenements, identite, lire, observer, verrou


ROOT = Path(__file__).resolve().parents[1]
LINUX = sys.platform == "linux" and Path("/proc/sys/kernel/random/boot_id").exists()


@unittest.skipUnless(LINUX, "Qualification AUT-02A : Linux /proc et flock seulement")
class SupervisionLocaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orka-aut02-test-")
        self.addCleanup(self.tmp.cleanup)
        self.destination = Path(self.tmp.name) / "recette"

    def creer(self, **options):
        return creer(self.destination, **options)

    def executer(self, hook=None, **options):
        return Controleur(self.destination, hook).run(**options)

    def registre(self):
        reg = Superviseur(self.destination / "registre.sqlite")
        self.addCleanup(reg.fermer)
        return reg

    def dossiers(self):
        return sorted((self.destination / "executions").iterdir())

    def tableau(self):
        return {t["id"]: t for t in etat(self.destination)["registre"]["taches"]}

    def crash(self, point, **options):
        self.creer(**options)
        script = ("import os,sys; from tools.supervision_locale.controleur import Controleur; "
                  "Controleur(sys.argv[1], lambda p: os._exit(89) if p==sys.argv[2] else None).run()")
        resultat = subprocess.run([sys.executable, "-B", "-c", script, str(self.destination), point],
                                  cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(resultat.returncode, 89, resultat.stdout + resultat.stderr)

    def attendre_travailleurs(self):
        fin = time.monotonic() + 5
        while time.monotonic() < fin:
            dossiers = self.dossiers()
            if dossiers and all((d / "termine.json").exists() for d in dossiers):
                if all(observer(lire(d / "demarre.json")["identite"]) != "actif" for d in dossiers):
                    return
            time.sleep(.01)
        self.fail("Le travailleur fixe ne s'est pas terminé")

    def test_nominal_trois_processus_reservations_et_preuves(self):
        self.creer()
        vrai_popen = subprocess.Popen
        lancements = []

        def lancer(argv, **kwargs):
            self.assertEqual(argv[:4], [sys.executable, "-I", "-B", str(TRAVAILLEUR)])
            self.assertNotIn("shell", kwargs)
            # La réservation doit exister AVANT l'appel système de lancement.
            reg = self.registre()
            actives = reg.etat(MISSION)["actives"]
            self.assertEqual(len(actives), 1)
            self.assertEqual(actives[0]["phase"], "reservee")
            lancements.append(actives[0]["id"])
            return vrai_popen(argv, **kwargs)

        with patch("subprocess.Popen", side_effect=lancer), patch("socket.socket", side_effect=AssertionError("Réseau interdit")):
            resultat = self.executer()
        self.assertEqual(resultat["etat"], "succes", resultat)
        self.assertEqual(resultat["appels_modeles"], 0)
        self.assertEqual(len(lancements), 3)
        self.assertEqual(lire(self.destination / "sorties/total.json"), {"total_net": 115})
        self.assertEqual(lire(self.destination / "sorties/bilan.json")["bilan"], "Total net vérifié : 115.")
        taches = self.tableau()
        self.assertEqual([taches[t]["tentatives"] for t in ("T1", "T2")], [2, 1])
        self.assertTrue(all(t["parametres_appliques_declares"] is None for t in taches.values()))
        for dossier in self.dossiers():
            preuve = lire(dossier / "arret.json")
            self.assertIn(observer(preuve["identite"]), ("arrete", "absent", "remplace"))
            self.assertEqual(preuve["appels_modeles"], 0)
        reg = self.registre()
        journal = reg.journal()
        self.assertEqual(sum(e["type"] == "reprise_preparee" for e in journal), 1)
        premiere = reg.db.execute("SELECT * FROM tentatives WHERE tache='T1' AND numero=1").fetchone()
        self.assertIsNone(premiere["observations"])
        self.assertFalse((self.destination / "executions" / premiere["id"] / "resultat.json").exists())
        self.assertEqual(etat(self.destination)["registre"]["actives"], [])
        self.assertEqual(self.executer()["etat"], "succes")
        self.assertEqual(len(self.dossiers()), 3)  # Reprise idempotente, pas une nouvelle mission.

    def test_refuse_destination_existante_et_ne_reinitialise_pas(self):
        self.creer()
        avant = (self.destination / "registre.sqlite").read_bytes()
        with self.assertRaises(FileExistsError):
            self.creer()
        self.assertEqual((self.destination / "registre.sqlite").read_bytes(), avant)

    def test_refuse_reprise_non_deleguee(self):
        self.creer(reprise=False)
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
        self.assertEqual(self.tableau()["T2"]["tentatives"], 0)

    def test_maximum_un_et_epuisement_deux(self):
        for nom, options, attendu in (("un", {"maximum": 1}, 1),
                                      ("deux", {"incident": "epuisement"}, 2)):
            with self.subTest(nom=nom):
                self.destination = Path(self.tmp.name) / nom
                self.creer(**options)
                self.assertEqual(self.executer()["etat"], "partiel")
                self.assertEqual(self.tableau()["T1"]["tentatives"], attendu)
                self.assertEqual(self.executer()["etat"], "partiel")
                self.assertEqual(len(self.dossiers()), attendu)

    def test_code_zero_ne_suffit_pas_et_erreur_permanente_non_reprise(self):
        for incident in ("erreur-permanente", "sortie-absente", "mauvais-total", "mauvais-type"):
            with self.subTest(incident=incident):
                self.destination = Path(self.tmp.name) / incident
                self.creer(incident=incident)
                resultat = self.executer()
                self.assertEqual(resultat["etat"], "partiel")
                self.assertEqual(resultat["registre"]["actives"], [])
                self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
                self.assertEqual(self.tableau()["T2"]["tentatives"], 0)
                self.assertFalse((self.destination / "sorties/total.json").exists())
                self.assertEqual(self.tableau()["T1"]["etat"], "bloquee")

    def test_silence_et_retour_tardif_arretes_sans_publication(self):
        for incident in ("silence", "retour-tardif"):
            with self.subTest(incident=incident):
                self.destination = Path(self.tmp.name) / incident
                self.creer(incident=incident, delai=.2)
                resultat = self.executer()
                self.assertEqual(resultat["etat"], "partiel")
                self.assertEqual(resultat["registre"]["actives"], [])
                dossier, = self.dossiers()
                preuve = lire(dossier / "arret.json")
                self.assertTrue(preuve["timeout"])
                self.assertLess(preuve["code"], 0)
                self.assertNotEqual(observer(preuve["identite"]), "actif")
                time.sleep(1.05)
                self.assertFalse((dossier / "resultat.json").exists())
                self.assertFalse((self.destination / "sorties/total.json").exists())
                self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
                if incident == "silence":
                    activites = evenements(self.destination / "controleur.jsonl")
                    self.assertFalse(any(e["type"] == "activite_observee" for e in activites))

    def test_crash_avant_lancement_reste_incertain_sans_doublon(self):
        for point in ("reservee", "intention"):
            with self.subTest(point=point):
                self.destination = Path(self.tmp.name) / point
                self.crash(point, delai=.1)
                for _ in range(2):
                    resultat = self.executer()
                    self.assertEqual(resultat["etat"], "partiel")
                    self.assertEqual(len(resultat["registre"]["actives"]), 1)
                    self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
                    self.assertFalse(any((d / "demarre.json").exists() for d in self.dossiers()))

    def test_crash_fenetres_puis_meme_base_sans_nouvelle_execution_cachee(self):
        for point in ("lancee", "rattachee", "arretee", "liberee", "reprise_preparee",
                      "publiee", "soumise", "acceptee"):
            with self.subTest(point=point):
                self.destination = Path(self.tmp.name) / point
                self.crash(point)
                self.attendre_travailleurs()
                resultat = self.executer()
                self.assertEqual(resultat["etat"], "succes", resultat)
                self.assertEqual([self.tableau()[t]["tentatives"] for t in ("T1", "T2")], [2, 1])
                self.assertEqual(len(self.dossiers()), 3)

    def test_travailleur_actif_adopte_et_non_remplace_apres_crash(self):
        self.crash("rattachee", incident="retour-tardif", delai=3)
        dossier, = self.dossiers()
        debut = lire(dossier / "demarre.json")
        self.assertEqual(observer(debut["identite"]), "actif")
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "succes", resultat)
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
        self.assertEqual(len(self.dossiers()), 2)

    def test_crash_apres_liberation_resultat_et_apres_derniere_acceptation(self):
        for point, compte in (("liberee", 2), ("liberee", 3), ("acceptee", 2)):
            with self.subTest(point=point, compte=compte):
                self.destination = Path(self.tmp.name) / (point + str(compte))
                self.creer()
                script = """import os,sys
from tools.supervision_locale.controleur import Controleur
compteur = 0
def point(p):
    global compteur
    if p == sys.argv[2]:
        compteur += 1
        if compteur == int(sys.argv[3]):
            os._exit(89)
Controleur(sys.argv[1], point).run()
"""
                resultat = subprocess.run([sys.executable, "-B", "-c", script, str(self.destination), point, str(compte)],
                                          cwd=ROOT, capture_output=True, text=True, timeout=10)
                self.assertEqual(resultat.returncode, 89, resultat.stderr)
                self.assertEqual(self.executer()["etat"], "succes")
                self.assertEqual(len(self.dossiers()), 3)

    def test_arret_orphelin_par_pidfd_si_disponible(self):
        if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
            self.skipTest("pidfd non exposé")
        self.crash("rattachee", incident="retour-tardif", delai=.2)
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(resultat["registre"]["actives"], [])
        preuve = lire(self.dossiers()[0] / "arret.json")
        self.assertTrue(preuve["timeout"])
        self.assertIn("pidfd", preuve["preuve"])

    def test_resultat_termine_tard_pendant_crash_non_publie(self):
        self.crash("rattachee", incident="retour-tardif", delai=.2)
        self.attendre_travailleurs()
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        preuve = lire(self.dossiers()[0] / "arret.json")
        self.assertEqual(preuve["code"], 0)
        self.assertTrue(preuve["timeout"])
        self.assertFalse((self.destination / "sorties/total.json").exists())

    def test_absence_recu_fin_ne_prouve_pas_absence_effets(self):
        self.crash("lancee")
        self.attendre_travailleurs()
        dossier, = self.dossiers()
        (dossier / "termine.json").unlink()
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)
        self.assertEqual(len(self.dossiers()), 1)

    def test_identite_inconnue_ne_declenche_aucun_signal(self):
        self.crash("lancee")
        self.attendre_travailleurs()
        with patch("tools.supervision_locale.processus.observer", return_value="inconnu"), \
                patch("signal.pidfd_send_signal", side_effect=AssertionError("Aucun signal autorisé")):
            resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)

    def test_sans_pidfd_ne_pretend_pas_arreter_orphelin(self):
        self.crash("rattachee", incident="retour-tardif", delai=.2)
        with patch("tools.supervision_locale.processus.hasattr", return_value=False, create=True):
            resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)
        self.assertFalse((self.dossiers()[0] / "arret.json").exists())
        self.attendre_travailleurs()

    def test_pid_reutilise_ne_tue_pas_autre_processus(self):
        self.crash("lancee")
        self.attendre_travailleurs()
        dossier, = self.dossiers()
        with patch("tools.supervision_locale.processus.observer", return_value="remplace"), \
                patch("signal.pidfd_send_signal", side_effect=AssertionError("Ne pas tuer le nouveau PID")):
            preuve = ProcessusFixes().stop(dossier)
        self.assertEqual(preuve["code"], 75)

    def test_suspension_persiste_et_exige_reprise_explicite(self):
        self.creer()

        def interrompre(point):
            if point == "liberee":
                raise KeyboardInterrupt

        self.assertEqual(self.executer(interrompre)["etat"], "partiel")
        self.assertTrue(lire(self.destination / "controle.json")["suspendue"])
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
        self.assertEqual(self.executer(reprendre_suspension=True)["etat"], "succes")
        self.assertEqual(self.tableau()["T1"]["tentatives"], 2)

    def test_suspension_sans_lancement(self):
        self.creer()
        suspendre(self.destination)
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.dossiers(), [])
        self.assertEqual(self.executer(reprendre_suspension=True)["etat"], "succes")

    def test_sigint_reel_suspend_et_arrete_enfant_possede(self):
        self.creer(incident="silence", delai=5)
        processus = subprocess.Popen([sys.executable, "-B", "-m", "tools.supervision_locale", "resume",
                                      "--destination", str(self.destination)], cwd=ROOT,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            limite = time.monotonic() + 5
            while not any((d / "demarre.json").exists() for d in self.dossiers()):
                self.assertLess(time.monotonic(), limite)
                time.sleep(.01)
            processus.send_signal(signal.SIGINT)
            sortie, erreur = processus.communicate(timeout=5)
        finally:
            if processus.poll() is None:
                processus.kill()
                processus.communicate(timeout=5)
        self.assertEqual(processus.returncode, 2, erreur)
        self.assertEqual(json.loads(sortie)["etat"], "partiel")
        self.assertTrue(lire(self.destination / "controle.json")["suspendue"])
        preuve = lire(self.dossiers()[0] / "arret.json")
        self.assertNotEqual(observer(preuve["identite"]), "actif")
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(len(self.dossiers()), 1)

    def test_regression_sigint_pendant_ouverture_sqlite_suspend(self):
        import fcntl
        self.creer()
        base = sqlite3.connect(self.destination / "registre.sqlite")
        base.execute("BEGIN EXCLUSIVE")
        processus = subprocess.Popen([sys.executable, "-B", "-m", "tools.supervision_locale", "resume",
                                      "--destination", str(self.destination)], cwd=ROOT,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            limite, pris = time.monotonic() + 3, False
            while time.monotonic() < limite and not pris:
                path = self.destination / "controleur.lock"
                if path.exists():
                    with path.open("a+") as flux:
                        try:
                            fcntl.flock(flux, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(flux, fcntl.LOCK_UN)
                        except BlockingIOError:
                            pris = True
                time.sleep(.01)
            self.assertTrue(pris)
            time.sleep(.1)
            processus.send_signal(signal.SIGINT)
            time.sleep(.1)
            base.rollback()
            sortie, erreur = processus.communicate(timeout=5)
        finally:
            base.close()
            if processus.poll() is None:
                processus.kill()
                processus.communicate(timeout=5)
        self.assertEqual(processus.returncode, 2, erreur)
        resultat = json.loads(sortie)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertIsNone(resultat["registre"])
        self.assertTrue(lire(self.destination / "controle.json")["suspendue"])
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.dossiers(), [])
        self.assertEqual(self.executer(reprendre_suspension=True)["etat"], "succes")

    def test_regression_interruption_sans_objet_registre(self):
        self.creer()
        with patch("tools.supervision_locale.controleur.Superviseur", side_effect=KeyboardInterrupt):
            resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertIsNone(resultat["registre"])
        self.assertTrue(lire(self.destination / "controle.json")["suspendue"])
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.dossiers(), [])

    def test_regression_reboot_sans_recu_ne_reutilise_pas_echeance(self):
        self.crash("intention")
        with patch("tools.supervision_locale.stockage.demarrage_machine", return_value="autre-boot", create=True), \
                patch("tools.supervision_locale.controleur.time.monotonic", return_value=1.), \
                patch("tools.supervision_locale.controleur.time.sleep", side_effect=AssertionError("Attente entre deux boots")), \
                patch("subprocess.Popen", side_effect=AssertionError("Nouveau lancement interdit")):
            resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
        self.assertFalse(any((d / "demarre.json").exists() for d in self.dossiers()))

    def test_regression_adaptateur_reboot_et_boot_absent_refuses(self):
        self.crash("intention")
        dossier, = self.dossiers()
        with patch("tools.supervision_locale.stockage.demarrage_machine", return_value="autre-boot", create=True), \
                patch("tools.supervision_locale.processus.time.monotonic", return_value=1.), \
                patch("tools.supervision_locale.processus.time.sleep", side_effect=AssertionError("Attente inter-boot")):
            self.assertIsNone(ProcessusFixes().reconcile(dossier))
        spec = lire(dossier / "requete.json")
        spec.pop("demarrage_machine", None)
        ecrire(dossier / "requete.json", spec)
        with patch("tools.supervision_locale.processus.time.monotonic", return_value=1.), \
                patch("tools.supervision_locale.processus.time.sleep", side_effect=AssertionError("Boot non déclaré")):
            self.assertIsNone(ProcessusFixes().reconcile(dossier))

    def test_regression_wait_apres_kill_retourne_partiel_sans_fausse_preuve(self):
        self.creer(incident="silence", delai=.2)
        controleur = Controleur(self.destination)
        try:
            # Ni l'attente bloquante ni le sondage non bloquant ne confirment la fin.
            with patch.object(subprocess.Popen, "wait", side_effect=subprocess.TimeoutExpired("travailleur-fixe", 1)), \
                    patch.object(subprocess.Popen, "poll", return_value=None):
                resultat = controleur.run()
        finally:
            for enfant in controleur.adaptateur.enfants.values():
                if enfant.poll() is None:
                    enfant.kill()
                enfant.wait(timeout=3)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)
        self.assertTrue(resultat["arrets_non_confirmes"])
        self.assertFalse((self.dossiers()[0] / "arret.json").exists())
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)
        json.dumps(resultat)  # La CLI peut rendre l'état au lieu d'un traceback.

    def test_regression_nettoyage_sans_recu_tolere_wait_non_confirme(self):
        self.creer()
        dossier = self.destination / "executions" / "logiciel-simule"
        dossier.mkdir()
        enfant = Mock()
        enfant.poll.return_value = None
        enfant.wait.side_effect = subprocess.TimeoutExpired("logiciel-simule", 1)
        adaptateur = ProcessusFixes()
        adaptateur.enfants[str(dossier)] = enfant
        with patch("tools.supervision_locale.processus.time.sleep"), \
                patch("tools.supervision_locale.processus.time.monotonic", side_effect=[0., 2.]):
            incomplets = adaptateur.fermer()
        self.assertEqual(incomplets, [str(dossier)])
        enfant.kill.assert_called_once()
        self.assertFalse((dossier / "arret.json").exists())

    def test_regression_nettoyage_incomplet_interdit_succes(self):
        self.creer()
        controleur = Controleur(self.destination)
        fermer = controleur.adaptateur.fermer

        def incomplet():
            fermer()  # Récolter réellement les trois travailleurs avant la simulation.
            return [str(self.destination / "executions" / "inconnu-simule")]

        with patch.object(controleur.adaptateur, "fermer", side_effect=incomplet):
            resultat = controleur.run()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(resultat["arrets_non_confirmes"], ["inconnu-simule"])
        self.assertTrue(all(t["etat"] == "terminee" for t in resultat["registre"]["taches"]))

    def test_source_modifiee_avant_reprise_refusee(self):
        self.crash("liberee")
        (self.destination / "entree.csv").write_text("montant\n999\n")
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertIn("source modifiée", resultat["motif"])
        self.assertEqual(self.tableau()["T1"]["tentatives"], 1)

    def test_entree_changee_apres_publication_pas_acceptee(self):
        self.creer()

        def changer(point):
            if point == "publiee":
                (self.destination / "entree.csv").write_text("montant\n999\n")

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertNotEqual(self.tableau()["T1"]["etat"], "terminee")
        self.assertEqual(self.tableau()["T2"]["tentatives"], 0)

    def test_amont_change_apres_acceptation_bloque_aval(self):
        self.creer()

        def changer(point):
            if point == "acceptee":
                ecrire(self.destination / "sorties/total.json", {"total_net": 999})

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(self.tableau()["T1"]["validite"], "a_reexaminer")
        self.assertEqual(self.tableau()["T2"]["tentatives"], 0)

    def test_amont_change_apres_reservation_aval_refuse(self):
        self.creer()

        def changer(point):
            if point == "reservee" and (self.destination / "sorties/total.json").exists():
                ecrire(self.destination / "sorties/total.json", {"total_net": 999})

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(self.tableau()["T2"]["tentatives"], 1)
        self.assertNotEqual(self.tableau()["T2"]["etat"], "terminee")
        self.assertEqual(sum((d / "demarre.json").exists() for d in self.dossiers()), 2)

    def test_publication_modifiee_apres_soumission_refuse(self):
        self.creer()

        def changer(point):
            if point == "soumise":
                ecrire(self.destination / "sorties/total.json", {"total_net": 999})

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertNotEqual(self.tableau()["T1"]["etat"], "terminee")
        self.assertEqual(self.tableau()["T2"]["tentatives"], 0)

    def test_json_racine_non_objet_refuse_sans_acceptation(self):
        self.creer(incident="mauvais-total")

        def changer(point):
            if point == "arretee":
                ecrire(self.dossiers()[0] / "resultat.json", [115])

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertFalse((self.destination / "sorties/total.json").exists())
        self.assertEqual(self.tableau()["T1"]["etat"], "bloquee")

    def test_controleur_exclusif_entre_processus(self):
        self.creer()
        with verrou(self.destination):
            resultat = subprocess.run([sys.executable, "-B", "-m", "tools.supervision_locale", "resume",
                                       "--destination", str(self.destination)], cwd=ROOT,
                                      capture_output=True, text=True, timeout=5)
        self.assertEqual(resultat.returncode, 2)
        self.assertIn("déjà cette base", json.loads(resultat.stdout)["motif"])
        self.assertEqual(self.dossiers(), [])

    def test_verrou_remplace_interdit_lancement(self):
        self.creer()

        def changer(point):
            if point == "reservee":
                (self.destination / "controleur.lock").unlink()
                (self.destination / "controleur.lock").touch()

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(sum((d / "demarre.json").exists() for d in self.dossiers()), 0)

    def test_sortie_deplacee_hors_racine_ne_publie_pas(self):
        self.creer()
        ailleurs = Path(self.tmp.name) / "ailleurs"
        ailleurs.mkdir()

        def changer(point):
            if point == "arretee" and len(self.dossiers()) == 2:
                (self.destination / "sorties").rmdir()
                (self.destination / "sorties").symlink_to(ailleurs, target_is_directory=True)

        resultat = self.executer(changer)
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(list(ailleurs.iterdir()), [])

    def test_mandat_ou_code_change_refuse(self):
        self.creer()
        with patch("tools.supervision_locale.controleur.codes_sources", return_value={}):
            self.assertEqual(self.executer()["etat"], "partiel")
        config = lire(self.destination / "mission.json")
        config["reprise_autorisee"] = False
        ecrire(self.destination / "mission.json", config)
        self.assertEqual(self.executer()["etat"], "partiel")
        self.assertEqual(self.dossiers(), [])

    def test_journal_tronque_bloque_sans_reset(self):
        self.creer()
        (self.destination / "controleur.jsonl").write_text('{"type":')
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertIn("tronqué", resultat["motif"])
        self.assertEqual(self.dossiers(), [])

    def test_requete_de_lancement_modifiee_refusee(self):
        self.crash("lancee")
        self.attendre_travailleurs()
        dossier, = self.dossiers()
        spec = lire(dossier / "requete.json")
        spec["numero"] = 2
        ecrire(dossier / "requete.json", spec)
        resultat = self.executer()
        self.assertEqual(resultat["etat"], "partiel")
        self.assertEqual(len(resultat["registre"]["actives"]), 1)

    def test_cli_nominal_et_resume(self):
        commande = [sys.executable, "-B", "-m", "tools.supervision_locale"]
        resultat = subprocess.run([*commande, "demo", "--scenario", "reprise-simple", "--destination",
                                  str(self.destination)], cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(resultat.returncode, 0, resultat.stderr + resultat.stdout)
        self.assertEqual(json.loads(resultat.stdout)["etat"], "succes")
        resultat = subprocess.run([*commande, "resume", "--destination", str(self.destination)],
                                  cwd=ROOT, capture_output=True, text=True, timeout=5)
        self.assertEqual(resultat.returncode, 0, resultat.stderr + resultat.stdout)
        self.assertEqual(len(self.dossiers()), 3)

    def test_base_endommagee_refusee_sans_creation_de_processus(self):
        self.creer()
        (self.destination / "registre.sqlite").write_bytes(b"pas une base sqlite")
        resultat = subprocess.run([sys.executable, "-B", "-m", "tools.supervision_locale", "resume",
                                  "--destination", str(self.destination)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=5)
        self.assertEqual(resultat.returncode, 2)
        self.assertEqual(json.loads(resultat.stdout)["etat"], "refuse")
        self.assertEqual(self.dossiers(), [])


class FrontierePortableTests(unittest.TestCase):
    def test_plateforme_non_qualifiee_refuse_avant_creation(self):
        with tempfile.TemporaryDirectory() as dossier:
            destination = Path(dossier) / "essai"
            with patch("sys.platform", "win32"), self.assertRaisesRegex(ValueError, "Linux"):
                creer(destination)
            self.assertFalse(destination.exists())

    def test_cli_aucune_commande_ni_modele_arbitraire(self):
        for option in ("--model", "--commande"):
            resultat = subprocess.run([sys.executable, "-B", "-m", "tools.supervision_locale", "demo",
                                      "--scenario", "reprise-simple", "--destination", "inutilise", option, "x"],
                                     cwd=ROOT, capture_output=True, text=True, timeout=5)
            self.assertEqual(resultat.returncode, 2)
            self.assertIn("unrecognized arguments", resultat.stderr)


if __name__ == "__main__":
    unittest.main()
