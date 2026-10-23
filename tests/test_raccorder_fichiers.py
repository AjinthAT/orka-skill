"""Software transport checks; no Docker, network, model or campaign fixtures."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools/raccorder_fichiers.py"
spec = importlib.util.spec_from_file_location("raccordement", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.adapter = Path(self.tmp.name) / "adapter.py"
        self.adapter.write_text(
            "import json,sys\n"
            "d=json.load(sys.stdin)\n"
            "print(json.dumps({'ok':True,'slot':sys.argv[-1],'requete':d},ensure_ascii=False))\n", encoding="utf-8")
        self.fingerprint = hashlib.sha256(self.adapter.read_bytes()).hexdigest()
        self.bridge = module.Bridge(self.adapter, self.fingerprint, "fixture-fixed")

    def send(self, method, params=None, identifier=1):
        return self.bridge.handle(dict(jsonrpc="2.0", id=identifier, method=method, params=params or {}))

    def ready(self, version="2025-11-25"):
        r = self.send("initialize", dict(protocolVersion=version, capabilities={}, clientInfo={"name":"software-fixture", "version":"1"}))
        self.bridge.handle(dict(jsonrpc="2.0", method="notifications/initialized"))
        return r

    def test_lifecycle_capabilities_and_no_extra_tools(self):
        self.assertIn("error", self.send("tools/list"))
        r = self.ready()
        self.assertEqual(r["result"]["capabilities"], {"tools":{}})
        self.assertNotIn("instructions", r["result"])
        tools = self.send("tools/list")["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["lister", "lire", "ecrire"])
        self.assertTrue(all(not t["inputSchema"]["additionalProperties"] for t in tools))
        self.assertIn("error", self.send("initialize"))
        self.assertIn("error", self.send("sampling/createMessage"))
        self.assertIn("error", self.send("tools/list", {"cursor":"other"}))

    def test_negotiation_uses_only_declared_supported_versions(self):
        r = self.ready("2026-07-28")
        self.assertEqual(r["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(self.send("ping")["result"], {})

    def test_old_protocol_negotiation_and_exact_fixed_binding(self):
        self.assertEqual(self.ready("2025-06-18")["result"]["protocolVersion"], "2025-06-18")
        r = self.send("tools/call", {"name":"ecrire", "arguments":{"chemin":"sorties/note.md", "contenu":"é\nligne"}})
        d = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(d["slot"], "fixture-fixed")
        self.assertEqual(d["requete"], {"action":"ecrire", "chemin":"sorties/note.md", "contenu":"é\nligne"})

    def test_execution_command_and_unknown_field_injection_refused_before_backend(self):
        self.ready()
        # A backend that fails if invoked makes these refusal checks meaningful.
        self.adapter.unlink()
        for name, args in [("lister", {"execution":"other"}), ("lire", {"chemin":"x", "command":"cat"}),
                           ("ecrire", {"chemin":{}, "contenu":"x"})]:
            r = self.send("tools/call", {"name":name, "arguments":args})
            self.assertEqual(r["result"]["content"][0]["text"], "Arguments refusés")
        for params in [{"name":[]}, {"name":"exec"}, {"name":"lister", "execution":"other"}]:
            self.assertIn("error", self.send("tools/call", params))

    def test_adapter_changes_are_not_executed(self):
        self.ready()
        marker = self.adapter.parent / "executed"
        self.adapter.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n", encoding="utf-8")
        r = self.send("tools/call", {"name":"lister", "arguments":{}})
        self.assertTrue(r["result"]["isError"])
        self.assertFalse(marker.exists())
        with self.assertRaises(ValueError):
            module.Bridge(self.adapter, self.fingerprint, "fixture-fixed")

    def test_backend_refusals_and_failures_are_tool_errors(self):
        for body in ["print('{\"ok\":false}');raise SystemExit(2)", "print('not json')", "raise SystemExit(1)"]:
            self.adapter.write_text(body, encoding="utf-8")
            b = module.Bridge(self.adapter, hashlib.sha256(self.adapter.read_bytes()).hexdigest(), "fixture-fixed")
            self.assertTrue(b.call("lister", {})["isError"])

    def test_notifications_never_execute_a_tool(self):
        self.ready()
        self.adapter.unlink()
        self.assertIsNone(self.bridge.handle({"jsonrpc":"2.0", "method":"tools/call", "params":{"name":"lister"}}))
        self.assertIsNone(self.bridge.handle({"jsonrpc":"2.0", "method":"notifications/cancelled", "params":{}}))

    def test_malformed_frames_recover_without_leaking_diagnostics(self):
        raw = b'[]\n{\n{"jsonrpc":"2.0","id":1,"method":"ping","method":"tools/list"}\n\xff\n'
        destination = io.BytesIO()
        module.serve(self.bridge, io.BytesIO(raw), destination)
        rows = [json.loads(x) for x in destination.getvalue().splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all("error" in r for r in rows))
        self.assertNotIn(str(self.adapter), destination.getvalue().decode())

    def test_oversized_frame_is_not_reinterpreted(self):
        out = io.BytesIO()
        module.serve(self.bridge, io.BytesIO(b"x"*(module.MAX_MESSAGE+3)+b'\n{"jsonrpc":"2.0","id":1,"method":"ping"}\n'), out)
        self.assertEqual(len(out.getvalue().splitlines()), 1)

    def test_real_stdio_process_has_only_jsonrpc_stdout_and_exits_on_eof(self):
        messages = [{"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{"protocolVersion":"2025-11-25", "capabilities":{}, "clientInfo":{"name":"fixture","version":"1"}}},
                    {"jsonrpc":"2.0", "method":"notifications/initialized"},
                    {"jsonrpc":"2.0", "id":2, "method":"tools/call", "params":{"name":"lister", "arguments":{}}},
                    {"jsonrpc":"2.0", "id":3, "method":"tools/call", "params":{"name":"ecrire", "arguments":{"chemin":"sorties/note.md", "contenu":"é\nligne"}}}]
        raw = b"\n".join(module.encode(m) for m in messages)+b"\n"
        r = subprocess.run([sys.executable,"-I","-B",str(SCRIPT),"--adapter",str(self.adapter),
                            "--empreinte-adaptateur",self.fingerprint,"--execution","fixture-fixed"], input=raw, capture_output=True, timeout=10)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr, b"")
        rows = [json.loads(x) for x in r.stdout.splitlines()]
        self.assertEqual([r["id"] for r in rows], [1, 2, 3])
        self.assertFalse(rows[1]["result"]["isError"])
        self.assertEqual(json.loads(rows[2]["result"]["content"][0]["text"])["requete"]["contenu"], "é\nligne")


if __name__ == "__main__":
    unittest.main()
