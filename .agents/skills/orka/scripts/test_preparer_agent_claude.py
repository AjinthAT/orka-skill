"""Regressions RH Claude hors ligne ; aucun lancement d'agent ou de modele."""

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from preparer_agent import REFERENCES, SKILL_ROOT, empreinte_requete, preparer as preparer_codex
from preparer_agent_claude import preparer


class ClaudePreparationTests(unittest.TestCase):
    def setUp(self):
        self.mandat = json.loads((SKILL_ROOT / "assets/mandat-exemple.json").read_text(encoding="utf-8"))
        self.claude = json.loads((REFERENCES / "profils-modeles-claude.json").read_text(encoding="utf-8"))
        self.codex = json.loads((REFERENCES / "profils-modeles.json").read_text(encoding="utf-8"))

    def definition(self, requete):
        agents = requete["parametres_demandes"]["agents"]
        self.assertEqual(len(agents), 1)
        nom, definition = next(iter(agents.items()))
        self.assertRegex(nom, r"^[a-z0-9-]+$")
        self.assertEqual(set(definition), {"description", "prompt", "model", "effort"})
        return nom, definition

    def test_catalogue_preserves_roles_teams_and_profile_names(self):
        self.assertEqual(self.claude["roles"], self.codex["roles"])
        self.assertEqual(self.claude["equipes"], self.codex["equipes"])
        self.assertEqual(set(self.claude["profils"]), set(self.codex["profils"]))
        self.assertEqual(self.claude["verification_documentaire"], "2026-10-23")
        for efforts in self.claude["modeles"].values():
            self.assertEqual(efforts, ["low", "medium", "high", "xhigh", "max"])

    def test_all_roles_receive_their_claude_profile_and_single_role_prompt(self):
        for role, profil in self.claude["roles"].items():
            with self.subTest(role=role):
                requete = preparer(dict(self.mandat, role=role, entrees=["simulation-v1.md"]))
                _, definition = self.definition(requete)
                self.assertEqual(definition["model"], self.claude["profils"][profil]["modele"])
                self.assertEqual(definition["effort"], self.claude["profils"][profil]["effort"])
                self.assertIn("## " + role, definition["prompt"])
                self.assertEqual(requete["profil"], profil)

    def test_export_is_native_requested_not_applied_and_never_mutates_mandate(self):
        original = deepcopy(self.mandat)
        requete = preparer(self.mandat)
        _, definition = self.definition(requete)
        self.assertEqual(self.mandat, original)
        self.assertEqual(requete["format"], "orka-claude-agent-definitions")
        self.assertEqual(requete["hote"], "claude")
        self.assertEqual(requete["etat"], "prepare_non_lance")
        self.assertIsNone(requete["parametres_appliques"])
        self.assertEqual(requete["verification_capacites"], "a_verifier_au_lancement")
        self.assertEqual(requete["empreinte_requete"], empreinte_requete(requete["parametres_demandes"]))
        self.assertNotIn("fork_turns", requete["parametres_demandes"])
        self.assertNotIn("reasoning_effort", definition)
        self.assertNotIn("tools", definition)
        for critere in self.mandat["criteres"]:
            self.assertIn(critere, definition["prompt"])

    def test_explicit_model_effort_and_capabilities_are_respected(self):
        mandat = dict(self.mandat, profil="expertise", modele="claude-opus-5-5", effort="xhigh")
        requete = preparer(mandat, {"claude-opus-5-5": ["xhigh"]})
        _, definition = self.definition(requete)
        self.assertEqual(definition["model"], mandat["modele"])
        self.assertEqual(definition["effort"], "xhigh")
        self.assertEqual(requete["verification_capacites"], "declarees_par_appelant")

    def test_missing_fable_or_effort_refused_without_substitution(self):
        for mandat, capacites in ((dict(self.mandat, profil="expertise"), {"claude-opus-5-5": ["high"]}),
                                   (self.mandat, {"claude-haiku-5-5": ["low"]})):
            with self.assertRaisesRegex(ValueError, "indisponible"):
                preparer(mandat, capacites)

    def test_foreign_model_alias_ultra_and_ultracode_are_refused(self):
        for values in (dict(modele="gpt-6.1-sol"), dict(modele="sonnet"), dict(effort="ultra"),
                       dict(effort="ultracode"), dict(modele="claude-opus-inconnu")):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, "absent du catalogue"):
                preparer(dict(self.mandat, **values))

    def test_retries_and_effort_have_distinct_fingerprints_without_changing_criteria(self):
        first = preparer(self.mandat)
        effort = preparer(dict(self.mandat, effort="high"))
        retry = preparer(dict(self.mandat, tentative=2))
        self.assertEqual(first["empreinte_prompt"], effort["empreinte_prompt"])
        self.assertNotEqual(first["empreinte_requete"], effort["empreinte_requete"])
        self.assertNotEqual(first["empreinte_requete"], retry["empreinte_requete"])
        self.assertNotEqual(self.definition(first)[0], self.definition(retry)[0])

    def test_shared_validation_refuses_incomplete_reviews_unknown_fields_and_bad_attempts(self):
        for changes in (dict(role="qa", mode="revue", entrees=[]), dict(criteres=[]), dict(tentative=True),
                        dict(permission_supposee="everything"), dict(role="unknown")):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                preparer(dict(self.mandat, **changes))

    def test_codex_default_is_kept_and_rejects_claude_model(self):
        for role, profil in self.codex["roles"].items():
            requete = preparer_codex(dict(self.mandat, role=role, entrees=["simulation-v1.md"]))
            self.assertEqual(requete["version"], 2)
            self.assertNotIn("hote", requete)
            self.assertEqual(requete["parametres_demandes"]["model"], self.codex["profils"][profil]["modele"])
            self.assertEqual(requete["parametres_demandes"]["reasoning_effort"], self.codex["profils"][profil]["effort"])
            self.assertEqual(requete["parametres_demandes"]["fork_turns"], "none")
        with self.assertRaisesRegex(ValueError, "absent du catalogue"):
            preparer_codex(dict(self.mandat, modele="claude-sonnet-5-5"))

    def test_cli_handles_utf8_capabilities_exclusive_output_and_target_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mandat = dict(self.mandat, objectif="Étudier l'été à Montréal", sortie=str(root / "livrable.md"))
            source = root / "mandat.json"; source.write_text(json.dumps(mandat, ensure_ascii=False), encoding="utf-8")
            caps = root / "capacites.json"; caps.write_text('{"claude-haiku-5-5":["medium"]}', encoding="utf-8")
            output = root / "requete.json"
            command = [sys.executable, "-B", str(SKILL_ROOT / "scripts/preparer_agent_claude.py"),
                       "--mandat", str(source), "--capacites", str(caps), "--output", str(output)]
            env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0", PYTHONIOENCODING="ascii")
            result = subprocess.run(command, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            previous = output.read_bytes()
            self.assertIn(mandat["objectif"], self.definition(json.loads(previous))[1]["prompt"])
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(output.read_bytes(), previous)
            command[-1] = mandat["sortie"]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertFalse(Path(mandat["sortie"]).exists())

    def test_cli_refuses_duplicate_keys_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "mandat.json"
            source.write_text(json.dumps(self.mandat)[:-1] + ',"effort":"medium","effort":"high"}', encoding="utf-8")
            output = root / "requete.json"
            result = subprocess.run([sys.executable, "-B", str(SKILL_ROOT / "scripts/preparer_agent_claude.py"),
                                     "--mandat", str(source), "--output", str(output)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
