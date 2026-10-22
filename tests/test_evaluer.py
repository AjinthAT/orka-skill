"""Regressions L3 sur observations simulees ; aucun moteur ou agent lance."""

import copy
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools/evaluer.py"
spec = importlib.util.spec_from_file_location("orka_evaluer", SCRIPT)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def sauver(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def empreintes(racine):
    return {p.relative_to(racine).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in racine.rglob("*") if p.is_file() and not p.is_symlink()}


def creer_plan(dossier):
    dossier.mkdir()
    for n, s in {"ref.md": "Instructions fictives v1", "candidate.md": "Instructions fictives v2",
                 "prompt.txt": "Simulation : calculer total et marge, sans action exterieure.",
                 "entree.json": '{"quantite":20,"prix":6,"plafond":150}'}.items():
        (dossier / n).write_text(s, encoding="utf-8")
    p = dict(format=1, id="simulation-l3", origine="Fixture logicielle, aucun modele execute",
             hypothese="Figer et relire chaque repetition, sans choisir seulement la meilleure", nature="simulation", hote="fixture-locale",
             repetitions=3, max_executions=6, limites=["Aucun modele, agent, Web ou code inspecte execute"],
             versions=[dict(id="reference", provenance="Fausse version v1", instructions=["ref.md"], reglages_demandes=None),
                       dict(id="candidate", provenance="Fausse version v2", instructions=["candidate.md"], reglages_demandes=None)],
             cas=[dict(id="budget", origine="Cas fictif", usage="developpement", entrees=["entree.json"], prompt="prompt.txt",
                       criteres=[dict(id="total", description="Total exact 20 fois 6", obligatoire=True, type="json_egal", fichier="livrable.json", chemin=["total"], attendu=120),
                                 dict(id="marge", description="Marge dans la plage attendue", obligatoire=True, type="json_nombre", fichier="livrable.json", chemin=["marge"], minimum=30, maximum=30),
                                 dict(id="sens", description="Revue metier attribuee", obligatoire=True, type="revue")])])
    sauver(dossier / "plan.json", p)
    return p


def creer_resultat(dossier, m, i, etat="terminee", total=120, revue=True):
    dossier.mkdir()
    e = m["executions"][i]
    sauver(dossier / "livrable.json", dict(total=total, marge=30))
    r = dict(format=1, execution=e["id"], empreinte_execution=evaluation.empreinte_execution(m, e), nature=m["plan"]["nature"], etat=etat,
             provenance=dict(source="Observation construite pour un test logiciel", hote="fixture-locale", id_natif=None),
             sorties=["livrable.json"], ecarts=["Ecart fictif conserve"] if etat == "hors_protocole" else [],
             revues={"sens":dict(etat="satisfait", auteur="evaluateur-simule", source="Fixture de revue, pas un avis reel", preuve="Decision fictive pour tester la conservation")} if revue else {})
    sauver(dossier / "declaration.json", r)
    return r


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orka-test-evaluations-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.inputs = self.root / "entrees é"
        self.plan = creer_plan(self.inputs)
        self.campagne = evaluation.preparer(self.inputs / "plan.json", self.root / "campagnes")
        self.m = evaluation.charger(self.campagne / "manifest.json")

    def enregistrer(self, i, **options):
        dossier = self.root / f"observation-{i}"
        r = creer_resultat(dossier, self.m, i, **options)
        evaluation.enregistrer(self.campagne, r["execution"], dossier / "declaration.json")
        return dossier, r

    def test_preparation_freezes_complete_matrix_without_execution(self):
        b = evaluation.bilan(self.campagne)
        self.assertEqual(len(self.m["executions"]), 6)
        self.assertEqual({(e["cas"], e["version"], e["repetition"]) for e in self.m["executions"]},
                         {("budget", v, r) for v in ("reference", "candidate") for r in (1, 2, 3)})
        self.assertEqual(b["resume"]["preparees"], 6)
        self.assertEqual(b["resume"]["executees_reelles_declarees"], 0)
        self.assertIsNone(b["tokens_connus"])
        self.assertEqual(b["etat"], "partiel")
        self.assertEqual(self.m["plan"]["limites"], self.plan["limites"])
        for n, p in self.m["pieces"].items():
            self.assertEqual((self.campagne / p["copie"]).read_bytes(), (self.inputs / n).read_bytes())

    def test_prepared_snapshot_survives_source_change_and_relocation(self):
        (self.inputs / "entree.json").write_text("source maintenant differente", encoding="utf-8")
        cible = self.root / "copie deplacee"
        shutil.move(str(self.campagne), cible)
        self.assertEqual(evaluation.bilan(cible)["empreinte_campagne"], self.m["empreinte"])

    def test_duplicate_case_version_ids_unknown_fields_and_limits_rejected(self):
        variantes = []
        for key in ("cas", "versions"):
            p = copy.deepcopy(self.plan); p[key].append(copy.deepcopy(p[key][0])); variantes.append(p)
        p = copy.deepcopy(self.plan); p["surprise"] = True; variantes.append(p)
        p = copy.deepcopy(self.plan); p["max_executions"] = 5; variantes.append(p)
        p = copy.deepcopy(self.plan); p["repetitions"] = True; variantes.append(p)
        for p in variantes:
            with self.subTest(plan=p), self.assertRaises(ValueError):
                evaluation.valider_plan(p)

    def test_existing_campaign_even_empty_or_broken_link_is_preserved(self):
        avant = empreintes(self.campagne)
        with self.assertRaises(FileExistsError):
            evaluation.preparer(self.inputs / "plan.json", self.root / "campagnes")
        self.assertEqual(empreintes(self.campagne), avant)
        autre = self.root / "autre"; autre.mkdir()
        cible = autre / self.plan["id"]; cible.mkdir()
        with self.assertRaises(FileExistsError):
            evaluation.preparer(self.inputs / "plan.json", autre)
        cible.rmdir()
        try:
            cible.symlink_to(autre / "absent", target_is_directory=True)
        except OSError:
            self.skipTest("Creation de liens symboliques indisponible")
        with self.assertRaises(FileExistsError):
            evaluation.preparer(self.inputs / "plan.json", autre)
        self.assertTrue(cible.is_symlink())

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        for brut in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.subTest(brut=brut), self.assertRaises(ValueError):
                evaluation.decoder(brut)

    def test_modified_frozen_input_and_manifest_block_reports_and_imports(self):
        morceau = self.campagne / self.m["pieces"]["entree.json"]["copie"]
        original = morceau.read_bytes(); morceau.write_bytes(b"modification")
        with self.assertRaisesRegex(ValueError, "Piece figee"):
            evaluation.bilan(self.campagne)
        d = self.root / "recue"; r = creer_resultat(d, self.m, 0)
        with self.assertRaises(ValueError):
            evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        morceau.write_bytes(original)
        (self.campagne / "manifest.json").write_text('{"empreinte":"fausse"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            evaluation.bilan(self.campagne)

    def test_result_provenance_fingerprint_and_real_identity_are_required(self):
        d = self.root / "recue"; r = creer_resultat(d, self.m, 0)
        variantes = []
        for key in ("provenance", "empreinte_execution"):
            v = copy.deepcopy(r); del v[key]; variantes.append(v)
        for changement in ({"empreinte_execution":"fausse"}, {"etat":"preparee"}, {"execution":"inconnue"}, {"nature":"reelle"}):
            v = copy.deepcopy(r); v.update(changement); variantes.append(v)
        v = copy.deepcopy(r); v["provenance"]["source"] = ""; variantes.append(v)
        for v in variantes:
            sauver(d / "declaration.json", v)
            with self.subTest(resultat=v), self.assertRaises(ValueError):
                evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        p = copy.deepcopy(self.plan); p["id"] = "reel"; p["nature"] = "reelle"
        sauver(self.inputs / "reel.json", p)
        campagne = evaluation.preparer(self.inputs / "reel.json", self.root / "campagnes")
        m = evaluation.charger(campagne / "manifest.json")
        r = creer_resultat(self.root / "observation-reelle", m, 0)
        with self.assertRaises(ValueError):
            evaluation.enregistrer(campagne, r["execution"], self.root / "observation-reelle/declaration.json")

    def test_no_result_overwrite_and_raw_declaration_is_preserved(self):
        d, r = self.enregistrer(0)
        cible = self.campagne / "resultats" / r["execution"]
        self.assertEqual((cible / "declaration.json").read_bytes(), (d / "declaration.json").read_bytes())
        avant = empreintes(cible)
        with self.assertRaises(ValueError):
            evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        self.assertEqual(empreintes(cible), avant)

    def test_corrupted_record_output_or_original_receipt_is_rejected(self):
        self.enregistrer(0)
        base = self.campagne / "resultats/e0001"
        for fichier in (base / "rapport.json", base / "declaration.json", base / "pieces/f0001"):
            original = fichier.read_bytes(); fichier.write_bytes(b"corrompu")
            with self.subTest(fichier=fichier), self.assertRaises(ValueError):
                evaluation.bilan(self.campagne)
            fichier.write_bytes(original)

    def test_mixed_repetitions_keep_every_outcome_and_denominator(self):
        self.enregistrer(0)
        self.enregistrer(1, total=121)
        self.enregistrer(2, etat="interrompue")
        self.enregistrer(3, etat="hors_protocole")
        self.enregistrer(4, revue=False)
        b = evaluation.bilan(self.campagne)
        r = b["resume"]
        for key, attendu in dict(prevues=6, preparees=1, terminees=3, interrompues=1, hors_protocole=1, evaluables=2, inconclusives=1, succes=1, echecs=1, observations_simulees=5, executees_reelles_declarees=0).items():
            self.assertEqual(r[key], attendu, key)
        self.assertEqual(r["succes_sur_evaluables"], dict(numerateur=1, denominateur=2, taux=0.5))
        self.assertEqual(r["succes_sur_prevues"]["denominateur"], 6)
        self.assertEqual(len(b["executions"]), 6)
        self.assertEqual(b["etat"], "partiel")
        self.assertEqual(sum(s["resume"]["prevues"] for s in b["series"]), 6)
        for s in b["series"]:
            for c in s["criteres"]:
                self.assertEqual(sum(c["comptes"].values()), 3)

    def test_checks_evaluate_structured_values_not_presence_of_a_phrase(self):
        d, _ = self.enregistrer(0, total=121)
        b = evaluation.bilan(self.campagne)
        self.assertEqual(b["executions"][0]["issue"], "echec")
        resultat = b["executions"][0]["criteres"][0]
        self.assertEqual(resultat["preuve"]["valeur"], 121)
        self.assertEqual(resultat["etat"], "non_satisfait")
        self.assertEqual(b["executions"][0]["criteres"][2]["methode"], "revue_attribuee")

    def test_missing_review_is_unknown_not_automatic_approval(self):
        self.enregistrer(0, revue=False)
        ligne = evaluation.bilan(self.campagne)["executions"][0]
        self.assertEqual(ligne["issue"], "inconclusive")
        self.assertEqual(ligne["criteres"][2]["etat"], "non_verifie")

    def test_malformed_missing_and_wrong_type_outputs_fail_deterministic_criteria(self):
        for i, contenu in enumerate((b"not-json", b'{"total":true,"marge":"30"}', b'{"autre":120}')):
            d = self.root / f"mauvais-{i}"; r = creer_resultat(d, self.m, i)
            (d / "livrable.json").write_bytes(contenu)
            evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        d = self.root / "absente"; r = creer_resultat(d, self.m, 3)
        r["sorties"] = []; sauver(d / "declaration.json", r)
        evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        b = evaluation.bilan(self.campagne)
        self.assertEqual(b["resume"]["echecs"], 4)

    def test_host_or_observed_setting_mismatch_is_not_comparable(self):
        for i in (0, 1):
            d = self.root / f"ecart-{i}"; r = creer_resultat(d, self.m, i)
            if i == 0:
                r["provenance"]["hote"] = "autre-hote"
            else:
                r["ecarts"] = ["Lecture hors perimetre signalee"]
            sauver(d / "declaration.json", r)
            evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        b = evaluation.bilan(self.campagne)
        self.assertEqual(b["resume"]["hors_protocole"], 2)
        self.assertEqual(b["resume"]["evaluables"], 0)
        self.assertEqual(b["resume"]["succes"], 0)

    def test_partial_measurements_unknowns_currencies_and_wall_duration(self):
        d = self.root / "mesure"; r = creer_resultat(d, self.m, 0)
        r.update(tokens=dict(id="mesure-1", source="compteur fictif exclusif", perimetre="execution_exclusive", entree=120, sortie=30),
                 cout=dict(nature="estime", montant="0.25", devise="EUR", source="exemple sans tarif reel"),
                 duree_observee=dict(secondes=9.5, nature="murale", source="horloge fictive"),
                 traces=dict(couverture="partielle", source="fixture de trace"))
        sauver(d / "declaration.json", r); evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        self.enregistrer(1)
        b = evaluation.bilan(self.campagne)
        self.assertEqual(b["couverture_mesures"]["denominateur"], 2)
        self.assertEqual(b["couverture_mesures"]["tokens_renseignes"], 1)
        self.assertEqual(b["tokens_connus"], dict(entree=120, sortie=30))
        self.assertIsNone(b["executions"][1]["mesures"]["tokens"])
        self.assertIsNone(b["executions"][0]["mesures"]["reglages_appliques"])
        self.assertEqual(b["couts_connus"], [dict(nature="estime", devise="EUR", sous_total_connu="0.25", renseignees=1)])
        self.assertEqual(b["executions"][0]["mesures"]["duree_observee"]["nature"], "murale")

    def test_duplicate_measure_id_and_cumulative_tokens_rejected(self):
        for i in (0, 1):
            d = self.root / f"mesure-{i}"; r = creer_resultat(d, self.m, i)
            r["tokens"] = dict(id="meme-id", source="fixture", perimetre="execution_exclusive", entree=1, sortie=2)
            sauver(d / "declaration.json", r)
            if i == 0:
                evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
            else:
                with self.assertRaises(ValueError):
                    evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
                r["tokens"]["perimetre"] = "cumulatif"; sauver(d / "declaration.json", r)
                with self.assertRaises(ValueError):
                    evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")

    def test_currencies_and_cost_natures_remain_separate(self):
        for i, devise, nature, montant in [(0, "EUR", "estime", "0.25"), (1, "USD", "constate", "0.10"), (2, "EUR", "constate", "0.50")]:
            d = self.root / f"cout-{i}"; r = creer_resultat(d, self.m, i)
            r["cout"] = dict(devise=devise, nature=nature, montant=montant, source="Valeur fictive exclusive")
            sauver(d / "declaration.json", r)
            evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        b = evaluation.bilan(self.campagne)
        self.assertEqual({(x["devise"], x["nature"], x["sous_total_connu"]) for x in b["couts_connus"]},
                         {("EUR", "estime", "0.25"), ("USD", "constate", "0.10"), ("EUR", "constate", "0.50")})
        self.assertEqual(b["couverture_mesures"]["couts_renseignes"], 3)

    def test_applied_settings_are_not_inferred_and_mismatch_is_preserved(self):
        p = copy.deepcopy(self.plan); p["id"] = "reglages"
        for v in p["versions"]:
            v["reglages_demandes"] = dict(modele="modele-fictif", effort="normal-fictif")
        sauver(self.inputs / "reglages.json", p)
        campagne = evaluation.preparer(self.inputs / "reglages.json", self.root / "campagnes")
        m = evaluation.charger(campagne / "manifest.json")
        for i in (0, 1):
            d = self.root / f"reglage-{i}"; r = creer_resultat(d, m, i)
            if i == 1:
                r["reglages_appliques"] = dict(modele="autre-fictif", effort="normal-fictif", source="Fixture native simulee")
            sauver(d / "declaration.json", r)
            evaluation.enregistrer(campagne, r["execution"], d / "declaration.json")
        b = evaluation.bilan(campagne)
        self.assertIsNone(b["executions"][0]["mesures"]["reglages_appliques"])
        self.assertEqual(b["executions"][1]["etat"], "hors_protocole")
        self.assertEqual(b["executions"][1]["mesures"]["reglages_appliques"]["modele"], "autre-fictif")

    def test_real_context_ids_cannot_relabel_an_existing_execution(self):
        p = copy.deepcopy(self.plan); p["id"] = "reelle-declaree"; p["nature"] = "reelle"
        sauver(self.inputs / "reelle.json", p)
        campagne = evaluation.preparer(self.inputs / "reelle.json", self.root / "campagnes")
        m = evaluation.charger(campagne / "manifest.json")
        for i in (0, 1):
            d = self.root / f"identite-{i}"; r = creer_resultat(d, m, i)
            r["provenance"]["id_natif"] = "identifiant-fictif-utilise-pour-un-test"
            sauver(d / "declaration.json", r)
            if i == 0:
                evaluation.enregistrer(campagne, r["execution"], d / "declaration.json")
            else:
                with self.assertRaisesRegex(ValueError, "Identifiant natif"):
                    evaluation.enregistrer(campagne, r["execution"], d / "declaration.json")

    def test_unsafe_paths_symlinks_and_executable_checks_are_refused(self):
        for nom in ("../prive", "/prive", "C:\\prive", "dossier/../prive", "https://exemple.invalid", "NUL.txt", "dossier./note"):
            with self.subTest(nom=nom), self.assertRaises(ValueError):
                evaluation.relatif(nom)
        p = copy.deepcopy(self.plan); p["cas"][0]["criteres"][0]["type"] = "commande"
        with self.assertRaises(ValueError):
            evaluation.valider_plan(p)
        lien = self.inputs / "lien.md"
        try:
            lien.symlink_to(self.inputs / "ref.md")
        except OSError:
            self.skipTest("Creation de liens symboliques indisponible")
        with self.assertRaises(ValueError):
            evaluation.lire(self.inputs, "lien.md")

    def test_prototypes_and_existing_register_are_never_executed_or_modified(self):
        marker = self.root / "code-execute"
        registre = self.inputs / "registre.sqlite"
        with closing(sqlite3.connect(registre)) as db:
            db.execute("CREATE TABLE preuves (texte TEXT)"); db.execute("INSERT INTO preuves VALUES ('historique')")
            db.commit()
        avant = empreintes(self.inputs)
        d = self.root / "prototype"; r = creer_resultat(d, self.m, 0)
        (d / "prototype.py").write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('execute')\n", encoding="utf-8")
        r["sorties"].append("prototype.py"); sauver(d / "declaration.json", r)
        brut = (d / "prototype.py").read_bytes()
        evaluation.enregistrer(self.campagne, r["execution"], d / "declaration.json")
        evaluation.bilan(self.campagne)
        self.assertFalse(marker.exists())
        self.assertEqual((d / "prototype.py").read_bytes(), brut)
        self.assertEqual(empreintes(self.inputs), avant)
        with closing(sqlite3.connect(registre)) as db:
            self.assertEqual(db.execute("SELECT texte FROM preuves").fetchall(), [("historique",)])

    def test_report_is_read_only_and_export_refuses_overwrite(self):
        self.enregistrer(0)
        avant = empreintes(self.root)
        evaluation.bilan(self.campagne)
        self.assertEqual(empreintes(self.root), avant)
        sortie = self.root / "bilan.json"; evaluation.ecrire(sortie, evaluation.bilan(self.campagne))
        brut = sortie.read_bytes()
        with self.assertRaises(FileExistsError):
            evaluation.ecrire(sortie, {})
        self.assertEqual(sortie.read_bytes(), brut)

    def test_captured_evaluation_bytes_survive_crlf_checkout(self):
        repo = SCRIPT.parents[1]
        if not (repo / ".git").exists() or shutil.which("git") is None:
            self.skipTest("Controle de checkout disponible seulement avec Git et son index")
        nom = "evals/contexte-L2-2026-10-22/criteres.json"
        destination = self.root / "checkout-crlf"; destination.mkdir()
        p = subprocess.run(["git", "-c", "core.autocrlf=true", "checkout-index", "--prefix", destination.as_posix() + "/", "--", nom],
                           cwd=repo, capture_output=True)
        self.assertEqual(p.returncode, 0, repr(p.stderr))
        self.assertEqual((destination / nom).read_bytes(), (repo / nom).read_bytes())

    def test_preserved_software_example_remains_consistent(self):
        base = SCRIPT.parents[1] / "evals/outillage-L3-2026-10-22"
        b = evaluation.bilan(base / "demonstration-simulee")
        self.assertEqual(b, evaluation.charger(base / "bilan.json"))
        self.assertEqual(b["resume"]["prevues"], 6)
        self.assertEqual(b["resume"]["executees_reelles_declarees"], 0)
        self.assertEqual(b["resume"]["succes_sur_evaluables"]["denominateur"], 2)
        for nom, h in evaluation.charger(base / "empreintes.json")["fichiers"].items():
            self.assertEqual(hashlib.sha256((base / nom).read_bytes()).hexdigest(), h, nom)

    def test_cli_uses_only_standard_library_with_utf8_and_no_hidden_launch(self):
        home = self.root / "home"; home.mkdir(); (home / "config.toml").write_text("personal=true")
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PYTHONIOENCODING="ascii:strict", PYTHONUTF8="0")
        avant = empreintes(self.root)
        p = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT), "bilan", "--campagne", str(self.campagne)], capture_output=True, env=env, cwd=self.root)
        self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8"))
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertEqual(r["resume"]["preparees"], 6)
        self.assertEqual(r["resume"]["executees_reelles_declarees"], 0)
        self.assertEqual(empreintes(self.root), avant)
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "bilan", "--campagne", str(self.root / "absente")], capture_output=True)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn(b"Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
