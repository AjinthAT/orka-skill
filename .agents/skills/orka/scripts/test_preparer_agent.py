"""Tests locaux de preparation ; aucun agent ni modele n'est lance."""

from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from preparer_agent import preparer, SKILL_ROOT


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.mandat = json.loads((SKILL_ROOT / "assets" / "mandat-exemple.json").read_text())

    def test_reglages_explicites_et_criteres_conserves(self):
        self.mandat.update(modele="gpt-6.1-sol", effort="high")
        original = deepcopy(self.mandat)
        resultat = preparer(self.mandat)
        args = resultat["parametres_demandes"]
        self.assertEqual(args["model"], "gpt-6.1-sol")
        self.assertEqual(args["reasoning_effort"], "high")
        self.assertEqual(args["fork_turns"], "none")
        for critere in self.mandat["criteres"]:
            self.assertIn(critere, args["message"])
        self.assertEqual(self.mandat, original)
        self.assertEqual(resultat["etat"], "prepare_non_lance")
        self.assertEqual(resultat["verification_capacites"], "a_verifier_au_lancement")

    def test_capacite_absente_refusee_sans_substitution(self):
        with self.assertRaisesRegex(ValueError, "indisponible"):
            preparer(self.mandat, {"gpt-6.1-sol": ["high"]})
        self.mandat["effort"] = "ultra"
        with self.assertRaisesRegex(ValueError, "effort absent"):
            preparer(self.mandat)

    def test_revue_exige_un_resultat_et_utilise_le_mode_revue(self):
        self.mandat["role"] = "qa"
        self.mandat.pop("mode")
        with self.assertRaisesRegex(ValueError, "revue exige"):
            preparer(self.mandat)
        self.mandat["entrees"] = ["resultat-fictif.md version v1, donnees de simulation"]
        self.assertEqual(preparer(self.mandat)["mode"], "revue")

    def test_profil_ne_remplace_pas_un_mode_explicite(self):
        self.mandat.update(role="qa", mode="correction", entrees=["anomalies.md v1"])
        self.assertEqual(preparer(self.mandat)["mode"], "correction")

    def test_reprise_et_correction_exigent_leurs_entrees(self):
        for mode in ("reprise", "correction"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    preparer(dict(self.mandat, mode=mode, entrees=[]))

    def test_tentatives_identifiees_sans_changer_la_tache(self):
        premiere = preparer(dict(self.mandat, tentative=1))
        seconde = preparer(dict(self.mandat, tentative=2))
        self.assertEqual(premiere["tache_id"], seconde["tache_id"])
        self.assertEqual(seconde["tentative"], 2)
        self.assertNotEqual(premiere["parametres_demandes"]["task_name"],
                            seconde["parametres_demandes"]["task_name"])
        for tentative in (0, -1, True, "2"):
            with self.subTest(tentative=tentative):
                with self.assertRaises(ValueError):
                    preparer(dict(self.mandat, tentative=tentative))

    def test_empreinte_distingue_parametres_et_prompt(self):
        premiere = preparer(self.mandat)
        seconde = preparer(dict(self.mandat, effort="high"))
        self.assertEqual(premiere["empreinte_prompt"], seconde["empreinte_prompt"])
        self.assertNotEqual(premiere["empreinte_requete"], seconde["empreinte_requete"])

    def test_cli_refuse_les_cles_json_dupliquees(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp)
            mandat = dossier / "mandat.json"
            contenu = json.dumps(self.mandat)
            mandat.write_text(contenu[:-1] + ', "effort": "medium", "effort": "high"}')
            sortie = dossier / "requete.json"
            resultat = subprocess.run(
                [sys.executable, "-B", str(SKILL_ROOT / "scripts" / "preparer_agent.py"),
                 "--mandat", str(mandat), "--output", str(sortie)],
                capture_output=True, text=True)
            self.assertEqual(resultat.returncode, 2)
            self.assertFalse(sortie.exists())

    def test_mandat_incomplet_ou_inconnu_refuse(self):
        for champ, valeur in (("criteres", []), ("objectif", ""), ("role", "inconnu")):
            with self.subTest(champ=champ):
                mandat = dict(self.mandat, **{champ: valeur})
                with self.assertRaises(ValueError):
                    preparer(mandat)
        with self.assertRaisesRegex(ValueError, "Champs inconnus"):
            preparer(dict(self.mandat, permission_supposee="tout"))

    def test_identifiants_distincts_meme_apres_normalisation(self):
        premier = preparer(dict(self.mandat, mission_id="a-b"))
        second = preparer(dict(self.mandat, mission_id="a_b"))
        self.assertNotEqual(premier["parametres_demandes"]["task_name"],
                            second["parametres_demandes"]["task_name"])

    def test_cli_necrase_ni_fichier_existant_ni_livrable(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp)
            mandat = dossier / "mandat.json"
            mandat.write_text(json.dumps(self.mandat))
            sortie = dossier / "requete.json"
            commande = [sys.executable, "-B", str(SKILL_ROOT / "scripts" / "preparer_agent.py"),
                        "--mandat", str(mandat), "--output", str(sortie)]
            subprocess.run(commande, check=True, capture_output=True, text=True)
            contenu = sortie.read_text()
            refus = subprocess.run(commande, capture_output=True, text=True)
            self.assertEqual(refus.returncode, 2)
            self.assertEqual(sortie.read_text(), contenu)
            self.mandat["sortie"] = str(dossier / "livrable.md")
            mandat.write_text(json.dumps(self.mandat))
            commande[-1] = self.mandat["sortie"]
            refus = subprocess.run(commande, capture_output=True, text=True)
            self.assertEqual(refus.returncode, 2)
            self.assertFalse(Path(self.mandat["sortie"]).exists())

    def test_les_roles_recoivent_uniquement_leur_fiche(self):
        catalogue = json.loads((SKILL_ROOT / "references" / "profils-modeles.json").read_text())
        for role in catalogue["roles"]:
            with self.subTest(role=role):
                mandat = dict(self.mandat, role=role, entrees=["simulation-v1.md"])
                requete = preparer(mandat)
                sections = re.findall(r"^## ([a-z][a-z-]+)",
                                      requete["parametres_demandes"]["message"], flags=re.M)
                self.assertEqual(sections, [role])


if __name__ == "__main__":
    unittest.main()
