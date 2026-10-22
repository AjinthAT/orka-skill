"""Regressions du diagnostic sur dossiers temporaires, sans installation personnelle."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("diagnostiquer.py")
spec = importlib.util.spec_from_file_location("orka_diagnostic", SCRIPT)
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)
META = '---\nname: orka\ndescription: Skill de test\nlicense: MIT\nmetadata:\n  version: "1.2.3"\n---\n'


def creer(racine):
    racine.mkdir()
    (racine / "SKILL.md").write_text(META + "# Test\n\n[Guide](GUIDE.md#demarrage)\n", encoding="utf-8")
    (racine / "GUIDE.md").write_text('# Demarrage\n\n[Retour](SKILL.md)\n[Web](https://example.invalid/unopened)\n', encoding="utf-8")
    (racine / "GUIDE.fr.md").write_text("# Guide français\n", encoding="utf-8")
    (racine / "LICENSE").write_text("MIT\n", encoding="utf-8")
    return racine


def empreintes(racine):
    return {p.relative_to(racine).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in racine.rglob("*") if p.is_file() and not p.is_symlink()}


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orka-test-diagnostic-")
        self.addCleanup(self.temp.cleanup)
        self.racine = Path(self.temp.name).resolve()
        self.skill = creer(self.racine / "installation é")

    def test_complete_relocated_and_reference_are_read_only(self):
        reference = self.racine / "reference"
        shutil.copytree(self.skill, reference)
        cible = self.racine / "autre emplacement"
        shutil.move(str(self.skill), cible)
        avant = empreintes(self.racine)
        rapport = diagnostic.diagnostiquer(cible, reference)
        self.assertEqual(rapport["code"], 0, rapport["constats"])
        self.assertEqual(rapport["integrite_reference"], "conforme")
        self.assertEqual(rapport["installation"]["version_declaree"], "1.2.3")
        self.assertEqual(empreintes(self.racine), avant)

    def test_missing_skill_stops_before_directory_scan(self):
        (self.skill / "SKILL.md").unlink()
        with patch.object(diagnostic.os, "scandir", side_effect=AssertionError("Aucun parcours sans SKILL.md")):
            rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 1)
        self.assertFalse(rapport["installation"]["inventaire_complet"])

    def test_metadata_formats_and_duplicates(self):
        for version in ('"1.2.3"', "'1.2.3'", "1.2.3"):
            with self.subTest(version=version):
                self.assertEqual(diagnostic.metadonnees(META.replace('"1.2.3"', version)), "1.2.3")
        invalides = [META.replace("name: orka", "name: autre"), META.replace("description: Skill de test", "description: |\n  multiline"),
                     META.replace("license: MIT", "license: MIT\nlicense: MIT"), META.replace('  version: "1.2.3"', '  version: "1.2.3"\n  version: "1.2.4"'),
                     META.replace('"1.2.3"', '"inconnue"'), META.replace("metadata:", "metadata: {}"), META.replace("---\n", "", 1),
                     META.replace("description: Skill de test", "description: 123"), META.replace("description: Skill de test", 'description: "   "')]
        for contenu in invalides:
            with self.subTest(contenu=contenu):
                (self.skill / "SKILL.md").write_text(contenu, encoding="utf-8")
                self.assertEqual(diagnostic.diagnostiquer(self.skill)["code"], 1)

    def test_missing_guide_and_local_resource_are_reported(self):
        (self.skill / "GUIDE.fr.md").unlink()
        (self.skill / "GUIDE.md").write_text('# Demarrage\n![Image](absente.png)\n<a href="manquant.md">Lien</a>\n', encoding="utf-8")
        rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 1)
        preuves = str(rapport["constats"])
        for nom in ("GUIDE.fr.md", "absente.png", "manquant.md"):
            self.assertIn(nom, preuves)

    def test_invalid_utf8_and_oversized_documents_are_reported(self):
        for contenu in (b"\xff", b"a" * (diagnostic.MAX_TEXTE + 1)):
            with self.subTest(octets=len(contenu)):
                (self.skill / "GUIDE.fr.md").write_bytes(contenu)
                rapport = diagnostic.diagnostiquer(self.skill)
                self.assertEqual(rapport["code"], 1)
                self.assertFalse(rapport["installation"]["inventaire_complet"])

    def test_anchors_and_reference_style_links(self):
        (self.skill / "GUIDE.md").write_text('# Demarrage\n[ici](#demarrage)\n[doc][x]\n[x]: GUIDE.fr.md\n```md\n[faux](absent.md)\n```\n', encoding="utf-8")
        self.assertEqual(diagnostic.diagnostiquer(self.skill)["code"], 0)
        with (self.skill / "GUIDE.md").open("a", encoding="utf-8") as flux:
            flux.write("[absent](GUIDE.fr.md#absent)\n")
        self.assertEqual(diagnostic.diagnostiquer(self.skill)["code"], 1)

    def test_local_adaptations_missing_and_extra_files_are_preserved(self):
        reference = self.racine / "reference"
        shutil.copytree(self.skill, reference)
        (self.skill / "GUIDE.fr.md").write_text("Ma personnalisation\n", encoding="utf-8")
        (self.skill / "notes.md").write_text("Mes notes\n", encoding="utf-8")
        (self.skill / "LICENSE").unlink()
        avant = empreintes(self.racine)
        rapport = diagnostic.diagnostiquer(self.skill, reference)
        self.assertEqual(rapport["code"], 1)
        self.assertEqual(rapport["integrite_reference"], "differente")
        comparaison = next(c for c in rapport["constats"] if c["id"] == "comparaison")["preuve"]
        self.assertEqual(comparaison, dict(manquants=["LICENSE"], supplementaires=["notes.md"], modifies=["GUIDE.fr.md"]))
        self.assertEqual(empreintes(self.racine), avant)

    def test_no_reference_never_asserts_integrity_or_host_activation(self):
        rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 0)
        self.assertEqual(rapport["integrite_reference"], "non_verifiee")
        self.assertEqual(rapport["activation_hote"], "non_verifiee")
        self.assertEqual(rapport["capacites_hote"], "non_verifiees")

    def test_invalid_reference_does_not_prove_integrity(self):
        rapport = diagnostic.diagnostiquer(self.skill, self.racine / "absente")
        self.assertEqual(rapport["code"], 1)
        self.assertEqual(rapport["integrite_reference"], "non_verifiee")

    def test_outside_links_are_not_read(self):
        secret = self.racine / "secret.md"
        secret.write_text("Ne pas lire\n", encoding="utf-8")
        with (self.skill / "GUIDE.md").open("a", encoding="utf-8") as flux:
            flux.write('[x](../secret.md)\n[y](%2e%2e/secret.md)\n[z](file:///private/secret.md)\n[w](C:\\secret.md)\n')
        original = diagnostic.ouvrir_local
        ouverts = []
        def ouvrir(racine, chemin):
            ouverts.append(chemin)
            self.assertTrue(chemin.is_relative_to(self.skill))
            return original(racine, chemin)
        with patch.object(diagnostic, "ouvrir_local", side_effect=ouvrir):
            rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 1)
        self.assertNotIn(secret, ouverts)

    def test_symlink_file_and_directory_are_not_followed(self):
        externe = self.racine / "hors-perimetre"
        externe.mkdir()
        (externe / "secret.md").write_text("Ne pas lire\n", encoding="utf-8")
        try:
            (self.skill / "lien.md").symlink_to(externe / "secret.md")
            (self.skill / "lien-dossier").symlink_to(externe, target_is_directory=True)
        except OSError:
            self.skipTest("Liens symboliques indisponibles")
        original = diagnostic.ouvrir_local
        ouverts = []
        def ouvrir(racine, chemin):
            ouverts.append(chemin)
            return original(racine, chemin)
        with patch.object(diagnostic, "ouvrir_local", side_effect=ouvrir):
            rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 1)
        self.assertFalse(any("lien" in p.name or "secret" in p.name for p in ouverts))
        self.assertTrue((self.skill / "lien-dossier").is_symlink())

    @unittest.skipUnless(os.name == "nt", "Jonctions Windows uniquement")
    def test_windows_junction_is_not_traversed(self):
        externe = self.racine / "hors-perimetre"
        externe.mkdir()
        jonction = self.skill / "jonction"
        proc = subprocess.run(["cmd", "/c", "mklink", "/J", str(jonction), str(externe)], capture_output=True)
        self.assertEqual(proc.returncode, 0, repr(proc.stderr))
        try:
            rapport = diagnostic.diagnostiquer(self.skill)
            self.assertEqual(rapport["code"], 1)
            self.assertFalse(rapport["installation"]["inventaire_complet"])
        finally:
            jonction.rmdir()

    def test_read_failure_is_reported_without_modification(self):
        original = diagnostic.ouvrir_local
        avant = empreintes(self.racine)
        def ouvrir(racine, chemin):
            if chemin.name == "GUIDE.fr.md":
                raise PermissionError("Lecture refusee")
            return original(racine, chemin)
        with patch.object(diagnostic, "ouvrir_local", side_effect=ouvrir):
            rapport = diagnostic.diagnostiquer(self.skill)
        self.assertEqual(rapport["code"], 1)
        self.assertFalse(rapport["installation"]["inventaire_complet"])
        self.assertIn("Lecture refusee", str(rapport["constats"]))
        self.assertEqual(empreintes(self.racine), avant)

    def test_inspected_scripts_never_execute_and_home_is_untouched(self):
        marker = self.racine / "executed"
        payload = "from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('executed')\n"
        (self.skill / "json.py").write_text(payload, encoding="utf-8")
        (self.skill / "run.py").write_text(payload, encoding="utf-8")
        home = self.racine / "home"
        home.mkdir()
        (home / "config.toml").write_text("personal = true\n", encoding="utf-8")
        avant = empreintes(self.racine)
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PYTHONIOENCODING="ascii:strict", PYTHONUTF8="0")
        proc = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT), "--skill-dir", str(self.skill), "--json"],
                              cwd=self.racine, env=env, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8"))
        rapport = json.loads(proc.stdout.decode("utf-8"))
        self.assertIn("é", rapport["installation"]["dossier"])
        self.assertFalse(marker.exists())
        self.assertEqual(empreintes(self.racine), avant)

    def test_cli_arguments_and_missing_target_exit_codes(self):
        for args, code in [([], 2), (["--skill-dir", str(self.racine / "absent"), "--json"], 1)]:
            with self.subTest(args=args):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True)
                self.assertEqual(proc.returncode, code)
                self.assertNotIn(b"Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
