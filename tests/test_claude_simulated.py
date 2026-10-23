"""Offline protocol and per-generation catalogue regressions; no model calls."""

import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prototype_sdk_inspect.claude_adapter import ClaudeAdapter, QUALIFIED, SYSTEM_PROMPT
from tools.prototype_sdk_inspect.claude_simulated import (
    MODEL, SimulatedClaudeTransport, SimulationRefused, request_tools, simulated_client, verify_request,
)
from tools.prototype_sdk_inspect.contract import decode, encode, sha
from tools.prototype_sdk_inspect.prepare import prepare
from test_claude_adapter import FakeSession


def request():
    return dict(model=MODEL, system=SYSTEM_PROMPT, messages=[dict(role="user", content="Fictif")], tools=request_tools())


class PortableTests(unittest.TestCase):
    def test_serialized_catalogue_rejects_extra_missing_duplicate_foreign_and_hosted_tools(self):
        verify_request(encode(request()))
        for tools in (request_tools()[:-1], request_tools() + [dict(type="web_search_20250305", name="web_search")],
                      [request_tools()[0]] * 3, [dict(item, name="mcp__other__" + str(i))
                                                for i, item in enumerate(request_tools())]):
            bad = request(); bad["tools"] = tools
            with self.subTest(tools=tools), self.assertRaises(SimulationRefused):
                verify_request(encode(bad))

    def test_serialized_catalogue_rejects_schema_description_and_envelope_drift(self):
        bads = []
        for key, value in (("additionalProperties", True), ("required", []), ("type", "array")):
            bad = request(); bad["tools"][1]["input_schema"][key] = value; bads.append(bad)
        for key, value in (("description", "Run shell"), ("name", "Bash"), ("type", "custom")):
            bad = request(); bad["tools"][1][key] = value; bads.append(bad)
        for key, value in (("model", "real-provider-model"), ("system", "Other"), ("messages", []),
                           ("mcp_servers", {})):
            bad = request(); bad[key] = value; bads.append(bad)
        for bad in bads:
            with self.subTest(bad=bad), self.assertRaises(SimulationRefused):
                verify_request(encode(bad))

    def test_duplicate_json_keys_nonfinite_and_malformed_requests_are_refused(self):
        for raw in (b'{"tools":[],"tools":[]}', b'NaN', b'[]', b'null', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                verify_request(raw)

    def test_import_does_not_load_a_provider_or_start_processes(self):
        import tools.prototype_sdk_inspect.claude_simulated as module

        with patch("subprocess.Popen", side_effect=AssertionError("No process")), \
                patch("socket.socket.connect", side_effect=AssertionError("No network")):
            spec = importlib.util.spec_from_file_location("tools.prototype_sdk_inspect._simulation_import", module.__file__)
            loaded = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(loaded)
            self.assertEqual(loaded.MODEL, MODEL)


@unittest.skipUnless(os.environ.get("ORKA_CLAUDE_SDK") == "1", "Opt-in pinned SDK with local simulated transport")
class SDKSimulationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import claude_agent_sdk

        self.session = FakeSession()
        self.adapter = ClaudeAdapter(self.session)
        self.addCleanup(self.adapter.close)
        for target in ("socket.socket.connect", "socket.socket.connect_ex", "subprocess.Popen", "anyio.open_process",
                       "asyncio.create_subprocess_exec", "claude_agent_sdk.query",
                       "claude_agent_sdk._internal.transport.subprocess_cli.SubprocessCLITransport.__init__"):
            guard = patch(target, side_effect=AssertionError("No network, CLI or default provider transport"))
            guard.start(); self.addCleanup(guard.stop)

    async def run_script(self, script, transform=None):
        async with asyncio.timeout(10):
            async with simulated_client(self.adapter, script) as (client, transport):
                if transform is not None:
                    transform(transport)
                await client.query("Simulation logicielle sans modèle")
                messages = [message async for message in client.receive_response()]
        return transport, messages

    async def test_real_sdk_control_routing_and_catalogue_checked_on_every_generation(self):
        script = [dict(tool=QUALIFIED[0], arguments={}),
                  dict(tool=QUALIFIED[1], arguments={"chemin": "entrees/fiche.md"}),
                  dict(tool=QUALIFIED[2], arguments={"chemin": "sorties/note.md", "contenu": "Été\n"}),
                  dict(text="Fin fictive")]
        counts = []

        def observe(transport):
            original = transport._rpc

            async def observed(method, *args, **kwargs):
                counts.append(method)
                return await original(method, *args, **kwargs)

            transport._rpc = observed

        transport, messages = await self.run_script(script, observe)
        self.assertFalse(messages[-1].is_error)
        self.assertEqual(len(transport.requests), 4)
        self.assertEqual(counts.count("tools/list"), 4)
        self.assertEqual(counts.count("tools/call"), 3)
        self.assertEqual([name for name, _ in self.session.calls], ["lister", "lire", "ecrire"])
        for raw, check in zip(transport.requests, transport.checks):
            verify_request(raw)
            self.assertEqual(check["request_sha256"], sha(raw))
            self.assertEqual(check["status"], "accepte")
        second = decode(transport.requests[1])["messages"]
        self.assertEqual(second[-2]["content"][0]["id"], second[-1]["content"][0]["tool_use_id"])
        self.assertIn("données fictives", str(second[-1]))

    async def test_late_mcp_catalogue_injection_stops_before_second_reply_or_write(self):
        def inject(transport):
            original = transport._rpc
            count = 0

            async def changed(method, *args, **kwargs):
                nonlocal count
                result = await original(method, *args, **kwargs)
                if method == "tools/list":
                    count += 1
                    if count == 2:
                        result["tools"].append(dict(name="bash", description="Bad", inputSchema={"type": "object"}))
                return result

            transport._rpc = changed

        transport, messages = await self.run_script([
            dict(tool=QUALIFIED[0], arguments={}),
            dict(tool=QUALIFIED[2], arguments={"chemin": "sorties/note.md", "contenu": "Forbidden"}),
            dict(text="Unreachable")], inject)
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual([name for name, _ in self.session.calls], ["lister"])
        self.assertEqual(transport.checks[-1]["status"], "refuse")

    async def test_last_serialized_boundary_rejects_drift_after_valid_mcp_listing(self):
        def inject(transport):
            original = transport._build_request

            def changed(catalogue, history):
                value = original(catalogue, history)
                if transport.requests:
                    value["tools"][1]["input_schema"]["additionalProperties"] = True
                return value

            transport._build_request = changed

        transport, messages = await self.run_script([
            dict(tool=QUALIFIED[0], arguments={}), dict(text="Must not be consumed")], inject)
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.checks[-1]["code"], "catalogue_refuse")
        self.assertEqual(len(self.session.calls), 1)

    async def test_options_checked_again_between_catalogue_and_script_sink(self):
        def inject(transport):
            original = transport._build_request

            def changed(catalogue, history):
                value = original(catalogue, history)
                transport._options.tools = ["Bash"]
                return value

            transport._build_request = changed

        transport, messages = await self.run_script([dict(text="Never")], inject)
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(transport.requests, ())
        self.assertEqual(self.session.calls, [])

    async def test_deadline_checked_after_catalogue_before_script_sink(self):
        def expire(transport):
            original = transport._build_request

            def changed(catalogue, history):
                value = original(catalogue, history)
                transport._deadline = 0
                return value

            transport._build_request = changed

        transport, messages = await self.run_script([dict(text="Never")], expire)
        self.assertEqual(messages[-1].result, "quota")
        self.assertEqual(transport.requests, ())
        self.assertEqual(self.session.calls, [])

    async def test_configuration_added_between_generations_is_refused(self):
        def inject(transport):
            original = self.session.call

            def changed(name, args):
                result = original(name, args)
                transport._options.mcp_servers["foreign"] = dict(type="stdio", command="bash")
                return result

            self.session.call = changed

        transport, messages = await self.run_script([
            dict(tool=QUALIFIED[0], arguments={}), dict(text="Never")], inject)
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(len(self.session.calls), 1)

    async def test_unknown_scripted_tool_cannot_reach_backend(self):
        transport, messages = await self.run_script([dict(tool="Bash", arguments={"command": "id"})])
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(messages[-1].result, "reponse_refusee")
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(self.session.calls, [])

    async def test_mcp_argument_refusal_is_preserved_in_following_request(self):
        transport, messages = await self.run_script([
            dict(tool=QUALIFIED[1], arguments={"chemin": True}), dict(text="Fin fictive")])
        self.assertFalse(messages[-1].is_error)
        self.assertTrue(decode(transport.requests[1])["messages"][-1]["content"][0]["is_error"])
        self.assertEqual(self.session.calls, [])

    async def test_script_and_recorded_catalogue_have_no_shared_mutable_state(self):
        script = [dict(tool=QUALIFIED[0], arguments={}), dict(text="Original")]

        def mutate(transport):
            script[0]["tool"] = "Bash"
            checks = transport.checks; checks.append(dict(status="fake"))

        transport, messages = await self.run_script(script, mutate)
        captured = decode(transport.requests[0]); captured["tools"].clear()
        verify_request(transport.requests[0])
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(len(transport.checks), 2)
        self.assertEqual(len(self.session.calls), 1)
        self.assertFalse(messages[-1].is_error)

    async def test_generation_limit_stops_before_ninth_request_without_retry(self):
        script = [dict(tool=QUALIFIED[0], arguments={}) for _ in range(8)] + [dict(text="Never")]
        transport, messages = await self.run_script(script)
        self.assertEqual(messages[-1].result, "quota")
        self.assertTrue(messages[-1].is_error)
        self.assertEqual(len(transport.requests), 8)
        self.assertEqual(len(self.session.calls), 8)
        self.assertEqual(transport.checks[-1]["generation"], 9)

    async def test_exhausted_script_and_host_errors_stop_with_redacted_result(self):
        transport, messages = await self.run_script([dict(tool=QUALIFIED[0], arguments={})])
        self.assertEqual(messages[-1].result, "script_epuise")
        self.assertEqual(len(transport.requests), 1)

        def broken(transport):
            transport._build_request = lambda *args: (_ for _ in ()).throw(OSError("/HOST_PRIVATE/key"))

        transport, messages = await self.run_script([dict(text="Never")], broken)
        self.assertEqual(messages[-1].result, "simulation_refusee")
        self.assertNotIn("HOST_PRIVATE", str(messages) + str(transport.checks))
        self.assertEqual(transport.requests, ())

    async def test_transport_cannot_reconnect_reset_or_accept_multiple_frames(self):
        options = self.adapter.options()
        transport = SimulatedClaudeTransport(self.adapter, options, [dict(text="Unused")])
        await transport.connect()
        with self.assertRaises(SimulationRefused):
            await transport.connect()
        with self.assertRaises(SimulationRefused):
            await transport.write('{}\n{}\n')
        self.assertFalse(transport.is_ready())
        await transport.close()
        with self.assertRaises(SimulationRefused):
            await transport.connect()
        self.assertEqual(transport.requests, ())

    async def test_second_user_query_cannot_reset_script_or_generation_count(self):
        async with simulated_client(self.adapter, [dict(text="Fin")]) as (client, transport):
            await client.query("First")
            _ = [m async for m in client.receive_response()]
            with self.assertRaises(SimulationRefused):
                await client.query("Second")
            self.assertEqual(len(transport.requests), 1)

    async def test_rpc_correlates_jsonrpc_response_and_times_out_without_retry(self):
        transport = SimulatedClaudeTransport(self.adapter, self.adapter.options(), [dict(text="Unused")])
        await transport.connect()
        try:
            task = asyncio.create_task(transport._rpc("tools/list"))
            frame = await transport._queue.get()
            await transport.write(encode(dict(type="control_response", response=dict(
                subtype="success", request_id=frame["request_id"], response=dict(mcp_response=dict(
                    jsonrpc="2.0", id="wrong", result={}))))).decode())
            with self.assertRaises(SimulationRefused):
                await task
            transport._deadline = 0
            with self.assertRaises(TimeoutError):
                await transport._rpc("tools/list")
            self.assertEqual(transport.requests, ())
        finally:
            await transport.close()

    async def test_closing_active_transport_cancels_before_any_scripted_write(self):
        transport = SimulatedClaudeTransport(self.adapter, self.adapter.options(), [dict(tool=QUALIFIED[2],
            arguments={"chemin": "sorties/note.md", "contenu": "Never"})])
        await transport.connect()
        await transport.write(encode(dict(type="control_request", request_id="init", request=dict(
            subtype="initialize", hooks=None, skills=[]))).decode())
        await transport.write(encode(dict(type="user", message=dict(role="user", content="Fictif"))).decode())
        await transport.close()
        self.assertTrue(transport._task.done())
        self.assertFalse(transport.is_ready())
        self.assertEqual(self.session.calls, [])


@unittest.skipUnless(os.environ.get("ORKA_CLAUDE_SDK") == "1" and os.environ.get("ORKA_P01_DOCKER") == "1",
                     "Opt-in simulated SDK transport to real isolated file worker")
class DockerSimulationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import subprocess
        from tools.prototype_sdk_inspect.claude_adapter import open_adapter

        self.open_adapter = open_adapter
        self.tmp = tempfile.TemporaryDirectory(prefix="orka-claude-simulation-")
        self.addCleanup(self.tmp.cleanup)
        self.root = prepare(Path(self.tmp.name) / "run", "hostile")
        real_popen = subprocess.Popen

        def docker_only(args, *positional, **kwargs):
            if type(args) is not list or args[0] != "docker" or kwargs.get("shell"):
                raise AssertionError("Only the operator-owned Docker backend is allowed")
            return real_popen(args, *positional, **kwargs)

        for target, effect in (("subprocess.Popen", docker_only), ("socket.socket.connect", AssertionError("No network")),
                               ("anyio.open_process", AssertionError("No process")),
                               ("claude_agent_sdk._internal.transport.subprocess_cli.SubprocessCLITransport.__init__",
                                AssertionError("No default transport"))):
            guard = patch(target, side_effect=effect)
            guard.start(); self.addCleanup(guard.stop)

    async def test_real_sdk_scripted_round_trip_through_mcp_to_docker(self):
        script = [dict(tool=QUALIFIED[0], arguments={}),
                  dict(tool=QUALIFIED[1], arguments={"chemin": "entrees/note.md"}),
                  dict(tool=QUALIFIED[2], arguments={"chemin": "sorties/note.md", "contenu": "Été fictif\n"}),
                  dict(tool=QUALIFIED[1], arguments={"chemin": "sorties/note.md"}), dict(text="Fin fictive")]
        with self.open_adapter(self.root) as adapter:
            async with simulated_client(adapter, script) as (client, transport):
                await client.query("Simulation indépendante de L4")
                messages = [m async for m in client.receive_response()]
                self.assertFalse(messages[-1].is_error)
                self.assertEqual(len(transport.requests), 5)
                last = decode(transport.requests[-1])
                self.assertIn("Été fictif", str(last["messages"][-1]))
                self.assertNotIn("controle/cas.json", str(decode(transport.requests[1])))
        self.assertEqual((self.root / "outputs/sorties/note.md").read_text(), "Été fictif\n")
        self.assertEqual(len((self.root / "controle/events.jsonl").read_bytes().splitlines()), 4)
        self.assertFalse(decode((self.root / "controle/stopped.json").read_bytes())["state"]["Running"])

    async def test_late_outgoing_catalogue_drift_prevents_real_file_write(self):
        script = [dict(tool=QUALIFIED[0], arguments={}),
                  dict(tool=QUALIFIED[2], arguments={"chemin": "sorties/note.md", "contenu": "Never"})]
        with self.open_adapter(self.root) as adapter:
            async with simulated_client(adapter, script) as (client, transport):
                original = transport._build_request

                def inject(catalogue, history):
                    value = original(catalogue, history)
                    if transport.requests:
                        value["tools"].append(dict(name="Bash", input_schema={"type": "object"}))
                    return value

                transport._build_request = inject
                await client.query("Simulation de dérive")
                messages = [m async for m in client.receive_response()]
                self.assertTrue(messages[-1].is_error)
                self.assertEqual(len(transport.requests), 1)
        self.assertEqual(list((self.root / "outputs/sorties").iterdir()), [])
        self.assertEqual(len((self.root / "controle/events.jsonl").read_bytes().splitlines()), 1)
        self.assertFalse(decode((self.root / "controle/stopped.json").read_bytes())["state"]["Running"])


if __name__ == "__main__":
    unittest.main()
