"""Tests logiciels sur donnees simulees, sans appel de modele."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bilan_agents import bilan


def tentative(tache="T1", numero=1, etat="accepte", mesure=None, cout=None):
    return {"tache": tache, "tentative": numero, "agent_id": "simulation-agent",
            "role": "analyste", "etat": etat, "preuve": "Constat simule pour le test",
            "mesure": mesure, "cout": cout}


def document(*lignes):
    return {"version": 1, "mission": "simulation", "couverture": "partielle", "tentatives": list(lignes)}


def mesure(identifiant="simulation-1", entree=100, sortie=20):
    return {"id": identifiant, "source": "Compteur simule", "perimetre": "tentative_exclusive",
            "entree": entree, "sortie": sortie}


def cout(montant="0.1", nature="constate", devise="EUR"):
    return {"montant": montant, "nature": nature, "devise": devise, "source": "Montant simule"}


class BilanTests(unittest.TestCase):
    def test_missing_usage_stays_unknown_and_empty_scope_has_no_rate(self):
        for entree in (document(), document(tentative(etat="non_revu"))):
            resultat = bilan(entree)
            self.assertIsNone(resultat["tokens"]["total_connu"])
            self.assertEqual(resultat["acceptation_initiale"], {"acceptees": 0, "revues": 0})
            self.assertEqual(resultat["couts"], [])

    def test_partial_usage_zero_and_reviews_have_explicit_denominators(self):
        entree = document(tentative(etat="a_corriger", mesure=mesure()),
                          tentative(numero=2, mesure=mesure("simulation-2", 0, 0)),
                          tentative("T2", etat="interrompu"), tentative("T3"))
        original = copy.deepcopy(entree)
        resultat = bilan(entree)
        self.assertEqual(resultat["reprises"], 1)
        self.assertEqual(resultat["acceptation_initiale"], {"acceptees": 1, "revues": 2})
        self.assertEqual(resultat["etats_taches"], {"accepte": 2, "interrompu": 1})
        self.assertEqual(resultat["tokens"], {"tentatives_mesurees": 2, "tentatives_sans_mesure": 2,
                         "entree_connue": 100, "sortie_connue": 20, "total_connu": 120})
        self.assertEqual(entree, original)

    def test_costs_use_exact_decimals_and_separate_currency_and_nature(self):
        resultat = bilan(document(tentative("T1", cout=cout("0.1")), tentative("T2", cout=cout("0.2")),
                                  tentative("T3", cout=cout("2", "estime")),
                                  tentative("T4", cout=cout("3", devise="USD")), tentative("T5")))
        self.assertEqual(resultat["couts"], [
            {"nature": "constate", "devise": "EUR", "montant": "0.3", "tentatives_renseignees": 2},
            {"nature": "constate", "devise": "USD", "montant": "3", "tentatives_renseignees": 1},
            {"nature": "estime", "devise": "EUR", "montant": "2", "tentatives_renseignees": 1}])
        self.assertEqual(resultat["tentatives_sans_cout"], 1)

    def test_duplicate_or_incomplete_attempt_history_is_refused(self):
        for entree in (document(tentative(), tentative()), document(tentative(numero=2)),
                       document(tentative(), tentative(numero=3))):
            with self.subTest(entree=entree), self.assertRaises(ValueError):
                bilan(entree)

    def test_overlapping_or_duplicate_measurements_are_refused(self):
        with self.assertRaises(ValueError):
            bilan(document(tentative(mesure=mesure()), tentative("T2", mesure=mesure())))
        for perimetre in ("cumulatif", "parent_avec_enfants"):
            valeur = dict(mesure(), perimetre=perimetre)
            with self.subTest(perimetre=perimetre), self.assertRaises(ValueError):
                bilan(document(tentative(mesure=valeur)))

    def test_invalid_counts_costs_and_unexpected_subtotals_are_refused(self):
        mauvaises_mesures = [mesure(entree=True), mesure(sortie=-1), mesure(entree=1.5),
                             dict(mesure(), raisonnement=10), dict(mesure(), source="")]
        for valeur in mauvaises_mesures:
            with self.subTest(mesure=valeur), self.assertRaises(ValueError):
                bilan(document(tentative(mesure=valeur)))
        for montant in (0.1, "NaN", "Infinity", "-1", "1e5", "1.0000000001"):
            with self.subTest(montant=montant), self.assertRaises(ValueError):
                bilan(document(tentative(cout=cout(montant))))
        for valeur in (cout(devise="eur"), cout(nature="facture_supposee"), dict(cout(), source="")):
            with self.subTest(cout=valeur), self.assertRaises(ValueError):
                bilan(document(tentative(cout=valeur)))

    def test_real_identity_provenance_and_known_fields_are_required(self):
        for champ, valeur in (("agent_id", ""), ("preuve", None), ("role", ""),
                               ("tentative", True), ("etat", "prepare"), ("modele_applique", ""),
                               ("tokens_devines", 100)):
            ligne = dict(tentative(), **{champ: valeur})
            with self.subTest(champ=champ), self.assertRaises(ValueError):
                bilan(document(ligne))
        for entree in (dict(document(), version=True), dict(document(), couverture="inconnue"),
                       dict(document(), tentatives=None), dict(document(), futur=True)):
            with self.assertRaises(ValueError):
                bilan(entree)

    def test_cli_reads_without_rewriting_and_rejects_duplicate_json_keys(self):
        script = Path(__file__).with_name("bilan_agents.py")
        with tempfile.TemporaryDirectory() as folder:
            entree = Path(folder) / "mesures.json"
            contenu = json.dumps(document(tentative()))
            entree.write_text(contenu, encoding="utf-8")
            resultat = subprocess.run([sys.executable, "-B", str(script), str(entree)],
                                      cwd=folder, capture_output=True, text=True)
            self.assertEqual(resultat.returncode, 0, resultat.stderr)
            self.assertEqual(json.loads(resultat.stdout)["tentatives"], 1)
            self.assertEqual(entree.read_text(encoding="utf-8"), contenu)
            self.assertEqual(list(Path(folder).iterdir()), [entree])
            entree.write_text('{"version": 1, "version": 2}', encoding="utf-8")
            resultat = subprocess.run([sys.executable, "-B", str(script), str(entree)],
                                      cwd=folder, capture_output=True, text=True)
            self.assertEqual(resultat.returncode, 2)
            self.assertEqual(resultat.stdout, "")
            self.assertIn("dupliquee", resultat.stderr)


if __name__ == "__main__":
    unittest.main()
