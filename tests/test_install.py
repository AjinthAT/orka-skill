import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("orka_install", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def test_copy_is_self_contained_and_helpers_run_after_relocation(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = installer.install(Path(folder) / "skills" / "orka")
            self.assertTrue((destination / "LICENSE").is_file())
            for _, relative in installer.skill_files():
                self.assertTrue((destination / relative).is_file(), str(relative))
            for script in ("test_preparer_agent.py", "test_superviser.py", "test_bilan_agents.py"):
                result = subprocess.run([sys.executable, "-B", str(destination / "scripts" / script)], cwd=folder, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "orka"
            destination.mkdir()
            sentinel = destination / "local.md"
            sentinel.write_text("Keep my changes", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(destination)
            self.assertEqual(sentinel.read_text(), "Keep my changes")
            self.assertEqual(list(destination.iterdir()), [sentinel])

    def test_broken_symlink_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "orka"
            try:
                destination.symlink_to(Path(folder) / "missing", target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable on this system")
            with self.assertRaises(FileExistsError):
                installer.install(destination)
            self.assertTrue(destination.is_symlink())

    def test_user_and_project_destinations(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            with patch.object(Path, "home", return_value=root):
                self.assertEqual(installer.destination_for("codex"), root / ".agents/skills/orka")
                self.assertEqual(installer.destination_for("claude"), root / ".claude/skills/orka")
            self.assertEqual(installer.destination_for("claude", root), root / ".claude/skills/orka")
            with self.assertRaises(ValueError):
                installer.destination_for("codex", root / "missing")

    def test_archive_has_one_skill_root_and_every_resource(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = installer.package(Path(folder) / "orka.zip")
            with ZipFile(destination) as archive:
                names = set(archive.namelist())
                expected = {"orka/" + relative.as_posix() for _, relative in installer.skill_files()}
                self.assertEqual(names, expected | {"orka/LICENSE"})
                self.assertEqual(archive.read("orka/SKILL.md"), (installer.SOURCE / "SKILL.md").read_bytes())
                self.assertIsNone(archive.testzip())
            with self.assertRaises(FileExistsError):
                installer.package(destination)

    def test_project_cannot_be_combined_with_custom_destination(self):
        result = subprocess.run([sys.executable, str(ROOT / "install.py"), "--destination", "unused", "--project", "."], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--project requires --agent", result.stderr)

    def test_cli_installs_both_project_targets_without_assistant_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            for agent, directory in (("codex", ".agents"), ("claude", ".claude")):
                result = subprocess.run([sys.executable, str(ROOT / "install.py"), "--agent", agent, "--project", folder], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((project / directory / "skills/orka/SKILL.md").is_file())
                self.assertEqual([entry.name for entry in (project / directory).iterdir()], ["skills"])


if __name__ == "__main__":
    unittest.main()
