"""P0/P1 software tests. Docker is opt-in; no SDK import or model call."""

from copy import deepcopy
import errno
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prototype_sdk_inspect import backend
from tools.prototype_sdk_inspect.contract import CONTRACT, CONTRACT_SHA, decode, encode, sha, validate_manifest
from tools.prototype_sdk_inspect.container import Session, create_command, docker, verify_container, verify_workspace
from tools.prototype_sdk_inspect.prepare import prepare


def manifest(inputs, outputs=None):
    return dict(format=1, run_id="a" * 32, contract_sha256=CONTRACT_SHA,
                inputs={k: dict(bytes=len(v), sha256=sha(v)) for k, v in inputs.items()},
                outputs=outputs or [f"sorties/{i}.md" for i in range(6)])


class ContractTests(unittest.TestCase):
    def test_exact_three_strict_schemas_and_limits(self):
        self.assertEqual(CONTRACT_SHA, "c4a408a9d8884d0de1b238641615897bcbe1940633e78645c12e8c8e947198d6")
        self.assertEqual([x["name"] for x in CONTRACT["tools"]], ["lister", "lire", "ecrire"])
        for tool in CONTRACT["tools"]:
            schema = tool["parameters"]
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(set(schema["required"]), set(schema["properties"]))
        self.assertEqual(CONTRACT["limits"]["calls"], 24)
        self.assertRegex(CONTRACT["image"], r"^python@sha256:[a-f0-9]{64}$")

    def test_manifest_rejects_schema_drift_unsafe_paths_and_types(self):
        good = manifest({"entrees/a.md": b"test"})
        for mutation in (dict(good, futur=True), dict(good, format=True), dict(good, run_id="other"),
                         dict(good, contract_sha256="0" * 64), dict(good, outputs=["../other"]),
                         dict(good, outputs=["sorties/a", "sorties/a"]),
                         dict(good, outputs=["sorties/a", "sorties/a/b"]),
                         dict(good, inputs={"entrees/a.md": {"sha256": "0" * 64, "bytes": True}})):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_manifest(mutation)
        for name in ("/tmp/x", "C:/x", "a/../x", "a/./x", "a//x", "a\\x", "a/%2e%2e/x", "a/é", "a/\x00"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_manifest(dict(good, outputs=[name]))

    def test_preparation_freezes_four_independent_cases_without_external_execution(self):
        with tempfile.TemporaryDirectory() as tmp, patch("subprocess.Popen", side_effect=AssertionError("No process")):
            for case in ("complet", "manquant", "contradiction", "hostile"):
                root = prepare(Path(tmp) / case, case)
                record = verify_workspace(root)
                self.assertEqual(record["case"], case)
                self.assertEqual(record["nature"], "simulation_logicielle")
                self.assertNotIn("expected", (root / "runtime/backend-manifest.json").read_text())
                self.assertNotIn("cas.json", [p.name for p in (root / "runtime").iterdir()])
                self.assertEqual(list((root / "outputs/sorties").iterdir()), [])
                with self.assertRaises(FileExistsError):
                    prepare(root, case)

    def test_dependency_lock_is_pinned_and_not_installed_by_preparation(self):
        metadata = decode((ROOT / "tools/prototype_sdk_inspect/dependency-lock.json").read_bytes())
        raw = (ROOT / "tools/prototype_sdk_inspect/requirements.lock").read_bytes()
        self.assertEqual(metadata["lock_sha256"], sha(raw))
        self.assertEqual(metadata["contract_sha256"], CONTRACT_SHA)
        self.assertEqual(metadata["direct"], {"openai-agents": "0.24.0", "inspect-ai": "0.3.283"})
        self.assertIn(b"--hash=sha256:", raw)
        self.assertNotIn("agents", sys.modules)
        self.assertNotIn("inspect_ai", sys.modules)
        folder = ROOT / "tools/prototype_sdk_inspect/cases"
        index = decode((folder / "index.json").read_bytes())
        self.assertEqual(index["revision"], "p01-cases-v1")
        for name, fingerprint in index["files"].items():
            self.assertEqual(sha((folder / name).read_bytes()), fingerprint)

    def test_workspace_tamper_and_extra_inputs_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("inputs/entrees/fiche.md", "runtime/backend.py", "controle/cas.json"):
                root = prepare(Path(tmp) / str(len(list(Path(tmp).iterdir()))), "complet")
                p = root / name
                p.chmod(0o600)
                p.write_text("Changed", encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ValueError):
                    verify_workspace(root)
            root = prepare(Path(tmp) / "extra", "complet")
            (root / "inputs/entrees/secret.md").write_text("Sentinel", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_workspace(root)

    def test_destination_links_and_source_links_are_preserved_and_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            link = root / "destination"
            try:
                link.symlink_to(root / "missing", target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            with self.assertRaises(FileExistsError):
                prepare(link, "complet")
            self.assertTrue(link.is_symlink())
            prepared = prepare(root / "prepared", "complet")
            p = prepared / "inputs/entrees/fiche.md"
            # Windows refuses unlink on the read-only fixture; enable this deliberate tamper.
            p.chmod(0o600)
            p.unlink()
            p.symlink_to(root / "missing")
            with self.assertRaises(ValueError):
                verify_workspace(prepared)

    def test_command_is_fixed_no_pull_no_network_and_dedicated_mounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepare(Path(tmp) / "prepared", "complet")
            args = create_command(root, "a" * 32)
            self.assertIn("--pull=never", args)
            self.assertEqual(args[args.index("--network") + 1], "none")
            self.assertEqual(args.count("--mount"), 3)
            self.assertNotIn(str(ROOT), args)
            self.assertNotIn("-e", args)

    def test_workspace_output_root_cannot_be_redirected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepare(Path(tmp) / "prepared", "complet")
            (root / "outputs/sorties").rmdir()
            (root / "outputs").rmdir()
            other = Path(tmp) / "outside"
            other.mkdir()
            try:
                (root / "outputs").symlink_to(other, target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            with self.assertRaises(ValueError):
                verify_workspace(root)


@unittest.skipUnless(sys.platform == "linux", "Backend requires Linux openat2; also run in the Docker suite")
class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inputs = self.root / "inputs"
        self.outputs = self.root / "outputs"
        (self.inputs / "entrees/nested").mkdir(parents=True)
        (self.outputs / "sorties").mkdir(parents=True)
        self.raw = "Été\nDonnées fictives.\n".encode()
        (self.inputs / "entrees/nested/a.md").write_bytes(self.raw)
        self.manifest = manifest({"entrees/nested/a.md": self.raw})
        self.worker = backend.Backend(self.inputs, self.outputs, self.manifest)
        self.addCleanup(self.worker.close)

    def call(self, name, args):
        return self.worker.handle(encode(dict(outil=name, arguments=args)))["resultat"]

    def test_utf8_round_trip_and_sha_match_actual_bytes(self):
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["donnees"]["contenu"].encode(), self.raw)
        value = "Été à Montréal\n"
        result = self.call("ecrire", {"chemin": "sorties/0.md", "contenu": value})
        self.assertEqual(result["donnees"]["sha256"], sha(value.encode()))
        self.assertEqual(self.call("lire", {"chemin": "sorties/0.md"})["donnees"]["contenu"], value)

    def test_listing_only_inventory_and_created_outputs(self):
        (self.inputs / "secret.txt").write_text("Invisible")
        result = self.call("lister", {})["donnees"]["fichiers"]
        self.assertEqual(len(result), 7)
        self.assertNotIn("secret.txt", str(result))
        self.assertFalse(next(x for x in result if x["chemin"] == "sorties/0.md")["disponible"])
        self.assertEqual(self.call("lire", {"chemin": "sorties/0.md"})["code"], "absent")

    def test_arguments_unknown_tools_and_duplicate_keys_have_no_effect(self):
        requests = [b'{"outil":"lister","outil":"lire","arguments":{}}', b'[]', b'NaN', b'\xff',
                    encode(dict(outil="bash", arguments={})), encode(dict(outil="lister", arguments={"cmd": "id"})),
                    encode(dict(outil="lire", arguments={"chemin": True})),
                    encode(dict(outil="lire", arguments={"chemin": "entrees/nested/a.md", "run_id": "other"}))]
        for raw in requests:
            with self.subTest(raw=raw):
                result = self.worker.handle(raw)
                self.assertFalse(result["resultat"]["ok"])
                self.assertNotIn(str(self.root), str(result))
        self.assertEqual(list((self.outputs / "sorties").iterdir()), [])

    def test_traversal_and_other_run_never_read_sentinel(self):
        (self.root / "private.md").write_text("PRIVATE SENTINEL")
        for path in ("../private.md", str(self.root / "private.md"), "C:/private.md", "//host/private.md",
                     "entrees/../private.md", "entrees/%2e%2e/private.md", "entrees\\private.md", "other/secret.md"):
            with self.subTest(path=path):
                result = self.call("lire", {"chemin": path})
                self.assertEqual(result["code"], "chemin_refuse")
                self.assertNotIn("PRIVATE SENTINEL", str(result))

    def test_source_writes_are_refused(self):
        self.assertEqual(self.call("ecrire", {"chemin": "entrees/nested/a.md", "contenu": "overwrite"})["code"], "chemin_refuse")
        self.assertEqual((self.inputs / "entrees/nested/a.md").read_bytes(), self.raw)

    def test_overwrite_and_revision_preserve_first_bytes(self):
        self.assertTrue(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "v1"})["ok"])
        self.assertEqual(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "v2"})["code"], "existe")
        self.assertTrue(self.call("ecrire", {"chemin": "sorties/1.md", "contenu": "v2"})["ok"])
        self.assertEqual((self.outputs / "sorties/0.md").read_bytes(), b"v1")

    def test_leaf_symlink_and_hardlink_refused_on_read(self):
        path = self.inputs / "entrees/nested/a.md"
        other = self.root / "other.md"
        other.write_bytes(self.raw)
        path.unlink()
        path.symlink_to(other)
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "fichier_refuse")
        path.unlink()
        os.link(other, path)
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "fichier_refuse")

    def test_parent_substituted_between_dispatch_and_open_is_not_followed(self):
        original = backend.open_beneath
        (self.root / "outside").mkdir()
        (self.root / "outside/a.md").write_bytes(b"PRIVATE SENTINEL")

        def raced(fd, name, flags, mode=0):
            (self.inputs / "entrees/nested").rename(self.inputs / "entrees/old")
            (self.inputs / "entrees/nested").symlink_to(self.root / "outside", target_is_directory=True)
            return original(fd, name, flags, mode)

        with patch.object(backend, "open_beneath", side_effect=raced):
            result = self.call("lire", {"chemin": "entrees/nested/a.md"})
        self.assertEqual(result["code"], "fichier_refuse")
        self.assertNotIn("PRIVATE SENTINEL", str(result))

    def test_write_parent_substitution_and_existing_links_do_not_touch_target(self):
        original = backend.open_beneath
        outside = self.root / "outside"
        outside.mkdir()

        def raced(fd, name, flags, mode=0):
            (self.outputs / "sorties").rename(self.outputs / "old")
            (self.outputs / "sorties").symlink_to(outside, target_is_directory=True)
            return original(fd, name, flags, mode)

        with patch.object(backend, "open_beneath", side_effect=raced):
            self.assertEqual(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "x"})["code"], "fichier_refuse")
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_leaf_symlink_and_hardlink_preserve_target(self):
        sentinel = self.root / "sentinel.md"
        sentinel.write_bytes(b"original")
        (self.outputs / "sorties/0.md").symlink_to(sentinel)
        os.link(sentinel, self.outputs / "sorties/1.md")
        for i in (0, 1):
            self.assertEqual(self.call("ecrire", {"chemin": f"sorties/{i}.md", "contenu": "x"})["code"], "existe")
        self.assertEqual(sentinel.read_bytes(), b"original")

    def test_fifo_is_nonblocking_and_refused(self):
        path = self.inputs / "entrees/nested/a.md"
        path.unlink()
        os.mkfifo(path)
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "fichier_refuse")

    def test_changed_input_and_output_detected(self):
        (self.inputs / "entrees/nested/a.md").write_bytes(b"Changed")
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "integrite")
        self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "First"})
        (self.outputs / "sorties/0.md").write_bytes(b"Changed")
        self.assertEqual(self.call("lire", {"chemin": "sorties/0.md"})["code"], "integrite")

    def test_caller_mutation_cannot_extend_frozen_permissions(self):
        self.manifest["outputs"].append("sorties/unauthorized.md")
        self.assertEqual(self.call("ecrire", {"chemin": "sorties/unauthorized.md", "contenu": "x"})["code"], "chemin_refuse")
        self.assertFalse((self.outputs / "sorties/unauthorized.md").exists())

    def test_failed_post_write_verification_never_accepts_the_output(self):
        original = self.worker.read

        def replaced(name):
            (self.outputs / name).write_bytes(b"substitution")
            return original(name)

        with patch.object(self.worker, "read", side_effect=replaced):
            self.assertEqual(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "initial"})["code"], "integrite")
        self.assertNotIn("sorties/0.md", self.worker.created)
        self.assertTrue(self.worker.closed)

    def test_quota_counts_refusals_and_closes_worker(self):
        for _ in range(CONTRACT["limits"]["calls"]):
            self.call("unknown", {})
        self.assertEqual(self.call("lister", {})["code"], "quota")
        self.assertEqual(self.call("lister", {})["code"], "ferme")

    def test_oversized_write_has_no_effect_and_closes_worker(self):
        result = self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "é" * 32769})
        self.assertEqual(result["code"], "quota")
        self.assertEqual(list((self.outputs / "sorties").iterdir()), [])
        self.assertTrue(self.worker.closed)

    def test_read_size_and_frame_size_are_bounded(self):
        (self.inputs / "entrees/nested/a.md").write_bytes(b"x" * (CONTRACT["limits"]["read_bytes"] + 1))
        self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "quota")
        self.assertEqual(self.worker.handle(b"x" * (CONTRACT["limits"]["request_bytes"] + 1))["resultat"]["code"], "ferme")

    def test_total_write_budget_cannot_be_reset_between_calls(self):
        for i in range(4):
            self.assertTrue(self.call("ecrire", {"chemin": f"sorties/{i}.md", "contenu": "a" * 65536})["ok"])
        self.assertEqual(self.call("ecrire", {"chemin": "sorties/4.md", "contenu": "x"})["code"], "quota")
        self.assertFalse((self.outputs / "sorties/4.md").exists())

    def test_interrupted_write_is_not_accepted_and_not_removed(self):
        real = os.fdopen

        class Broken:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self
            def __exit__(self, *args): self.stream.close()
            def fileno(self): return self.stream.fileno()
            def write(self, raw):
                self.stream.write(raw[:1]); self.stream.flush()
                raise OSError(errno.EIO, "Fake partial write")

        with patch.object(backend.os, "fdopen", side_effect=lambda fd, mode: Broken(real(fd, mode))):
            self.assertEqual(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "partial"})["code"], "erreur_io")
        self.assertEqual((self.outputs / "sorties/0.md").read_bytes(), b"p")
        self.assertNotIn("sorties/0.md", self.worker.created)
        self.assertTrue(self.worker.closed)

    def test_deadline_closes_without_file_effect(self):
        self.worker.deadline = 0
        self.assertEqual(self.call("ecrire", {"chemin": "sorties/0.md", "contenu": "x"})["code"], "quota")
        self.assertEqual(list((self.outputs / "sorties").iterdir()), [])

    def test_operation_timeout_closes_with_explicit_error(self):
        with patch.object(self.worker, "read", side_effect=TimeoutError("Simulated timeout")):
            self.assertEqual(self.call("lire", {"chemin": "entrees/nested/a.md"})["code"], "delai")
        self.assertTrue(self.worker.closed)

    def test_unsupported_openat2_never_falls_back(self):
        with patch.object(backend.sys, "platform", "unsupported"):
            with self.assertRaises(RuntimeError):
                backend.Backend(self.inputs, self.outputs, self.manifest)


@unittest.skipUnless(os.environ.get("ORKA_P01_DOCKER") == "1", "Opt-in offline Docker suite")
class DockerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orka-sdk-inspect-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = prepare(Path(self.tmp.name) / "run", "hostile")

    def test_full_linux_backend_regressions_in_networkless_container(self):
        run_id = uuid.uuid4().hex
        name = "orka-sdk-inspect-tests-" + run_id
        args = ["docker", "run", "--rm", "--pull=never", "--platform", CONTRACT["platform"], "--network", "none",
                "--name", name, "--label", CONTRACT["container"]["label"] + "=" + run_id,
                "--read-only", "--user", "65532:65532", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--pids-limit", "32", "--memory", "128m", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16777216",
                "--mount", f"type=bind,src={ROOT / 'tools/prototype_sdk_inspect'},dst=/src/tools/prototype_sdk_inspect,readonly",
                "--mount", f"type=bind,src={Path(__file__).resolve()},dst=/src/tests/test_prototype_sdk_inspect.py,readonly",
                CONTRACT["image"], "python", "-I", "-B", "-c",
                "import sys,unittest;sys.path.insert(0,'/src');sys.path.insert(0,'/src/tests');"
                "unittest.main(module='test_prototype_sdk_inspect',defaultTest='BackendTests',verbosity=2)"]
        try:
            result = subprocess.run(args, capture_output=True, timeout=45)
        finally:
            check = subprocess.run(["docker", "inspect", name], capture_output=True, timeout=10)
            if check.returncode == 0:
                info = decode(check.stdout)[0]
                self.assertEqual(info["Config"]["Labels"][CONTRACT["container"]["label"]], run_id)
                subprocess.run(["docker", "rm", "-f", name], check=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout.decode() + result.stderr.decode())
        self.assertIn(b"Ran 22 tests", result.stderr)
        self.assertNotIn(b"skipped", result.stderr)

    def test_actual_worker_mounts_network_protocol_and_confirmed_stop(self):
        with Session(self.root) as session:
            info = session.inspect()
            image = decode(docker("image", "inspect", CONTRACT["image"]))[0]
            verify_container(info, self.root, session.run_id, image)
            for field, value in (("NetworkMode", "bridge"), ("ReadonlyRootfs", False), ("Privileged", True)):
                altered = deepcopy(info)
                altered["HostConfig"][field] = value
                with self.assertRaises(ValueError):
                    verify_container(altered, self.root, session.run_id, image)
            listed = session.call("lister", {})
            self.assertTrue(listed["ok"])
            self.assertNotIn("cas.json", str(listed))
            self.assertNotIn("requirements.lock", str(listed))
            self.assertIn("Instruction hostile", session.call("lire", {"chemin": "entrees/note.md"})["donnees"]["contenu"])
            self.assertEqual(session.call("bash", {"command": "id"})["code"], "outil_inconnu")
            self.assertEqual(session.call_raw(b'{"outil":"lister","arguments":{},"arguments":{}}')["code"], "arguments_refuses")
            result = session.call("ecrire", {"chemin": "sorties/livrable.json", "contenu": "Été\n"})
            self.assertTrue(result["ok"])
            self.assertEqual(session.call("lire", {"chemin": "sorties/livrable.json"})["donnees"]["contenu"], "Été\n")
        stopped = decode((self.root / "controle/stopped.json").read_bytes())
        self.assertFalse(stopped["state"]["Running"])
        self.assertTrue(session.removed)
        with self.assertRaises(FileExistsError):
            Session(self.root)

    def test_two_workspaces_have_distinct_bindings_and_no_cross_reads(self):
        other = prepare(Path(self.tmp.name) / "other", "complet")
        first = Session(self.root)
        try:
            first.call("ecrire", {"chemin": "sorties/note.md", "contenu": "First sentinel"})
        finally:
            first.close()
        with Session(other) as second:
            self.assertNotEqual(first.run_id, second.run_id)
            self.assertEqual(second.call("lire", {"chemin": "sorties/note.md"})["code"], "absent")
            self.assertEqual(second.call("lire", {"chemin": "../run/outputs/sorties/note.md"})["code"], "chemin_refuse")

    def test_stopped_worker_is_not_replaced_or_retried(self):
        session = Session(self.root)
        docker("kill", session.name)
        with self.assertRaises(RuntimeError):
            session.call("lister", {})
        self.assertTrue(session.removed)
        self.assertFalse((self.root / "controle/events.jsonl").exists())

    def test_protocol_injection_and_timeout_close_without_hidden_operation(self):
        session = Session(self.root)
        with self.assertRaises(RuntimeError):
            session.call_raw(encode(dict(outil="lister", arguments={})) + b"\n{}")
        self.assertTrue(session.removed)
        other = prepare(Path(self.tmp.name) / "timeout", "complet")
        session = Session(other)
        with patch.object(session, "receive", side_effect=TimeoutError("Simulated client deadline")):
            with self.assertRaises(RuntimeError):
                session.call("lister", {})
        self.assertTrue(session.removed)
        self.assertFalse(decode((other / "controle/stopped.json").read_bytes())["state"]["Running"])


if __name__ == "__main__":
    unittest.main()
