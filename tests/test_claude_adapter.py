"""Offline Claude binding checks. SDK and Docker tests are separately opt-in."""

from contextlib import asynccontextmanager
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prototype_sdk_inspect import claude_adapter as binding
from tools.prototype_sdk_inspect.contract import CONTRACT_SHA, decode, sha
from tools.prototype_sdk_inspect.prepare import prepare


class FakeSession:
    """Explicit software double; actual file isolation is tested with Docker below."""

    def __init__(self):
        self.run_id = "a" * 32
        self.record = dict(run_id=self.run_id, contract_sha256=CONTRACT_SHA)
        self.calls = []

    def call(self, name, arguments):
        self.calls.append((name, deepcopy(arguments)))
        return dict(ok=True, code="ok", donnees={"sentinelle": "données fictives"})


@asynccontextmanager
async def mcp_client(adapter):
    import anyio
    from mcp.client.session import ClientSession
    from mcp.shared.memory import create_client_server_memory_streams

    server = adapter.options().mcp_servers[binding.SERVER]["instance"]
    async with create_client_server_memory_streams() as (client_streams, server_streams):
        async with anyio.create_task_group() as tasks:
            tasks.start_soon(server.run, *server_streams, server.create_initialization_options())
            async with ClientSession(*client_streams, read_timeout_seconds=5) as client:
                await client.initialize()
                binding.verify_catalogue(await client.list_tools())
                yield client
            tasks.cancel_scope.cancel()


def payload(result):
    return decode(result.content[0].text)


class PortableTests(unittest.TestCase):
    def test_separate_dependency_lock_preserves_backend_contract(self):
        directory = ROOT / "tools/prototype_sdk_inspect"
        metadata = decode((directory / "claude-dependency-lock.json").read_bytes())
        self.assertEqual(metadata["lock_sha256"], sha((directory / "requirements-claude.lock").read_bytes()))
        self.assertEqual(metadata["direct"], {"claude-agent-sdk": "0.2.173", "mcp": "2.3.0"})
        self.assertEqual(CONTRACT_SHA, "c4a408a9d8884d0de1b238641615897bcbe1940633e78645c12e8c8e947198d6")
        self.assertEqual(binding.NAMES, ("lister", "lire", "ecrire"))
        self.assertEqual(binding.QUALIFIED, ("mcp__orka__lister", "mcp__orka__lire", "mcp__orka__ecrire"))

    def test_import_is_lazy_without_sdk_or_external_operations(self):
        # Loading this module does not import SDKs, start a CLI or need network.
        with patch("subprocess.Popen", side_effect=AssertionError("No process")), \
                patch("socket.socket.connect", side_effect=AssertionError("No network")):
            name = "tools.prototype_sdk_inspect._claude_lazy_test"
            spec = importlib.util.spec_from_file_location(name, binding.__file__)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(module.NAMES, binding.NAMES)

    def test_dependency_drift_is_refused_before_worker_start(self):
        with patch.object(binding, "version", return_value="unexpected"), \
                patch.object(binding, "Session", side_effect=AssertionError("No Docker")):
            with self.assertRaises(RuntimeError):
                with binding.open_adapter("unused"):
                    self.fail("Must not open")


@unittest.skipUnless(os.environ.get("ORKA_CLAUDE_SDK") == "1", "Opt-in locked Claude SDK, no CLI or model")
class SDKTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Install/import happens before guards; tests themselves cannot call a model.
        import anyio
        import claude_agent_sdk

        self.session = FakeSession()
        self.adapter = binding.ClaudeAdapter(self.session)
        self.addCleanup(self.adapter.close)
        for target in ("socket.socket.connect", "subprocess.Popen", "asyncio.create_subprocess_exec",
                       "anyio.open_process", "claude_agent_sdk.query", "claude_agent_sdk.ClaudeSDKClient.connect"):
            guard = patch(target, side_effect=AssertionError("Offline test: forbidden network/CLI/model operation"))
            guard.start()
            self.addCleanup(guard.stop)

    async def test_actual_mcp_catalogue_is_exact_and_schemas_are_strict(self):
        async with mcp_client(self.adapter) as client:
            listed = await client.list_tools()
            binding.verify_catalogue(listed)
            self.assertEqual({item.name for item in listed.tools}, set(binding.NAMES))
            for item in listed.tools:
                self.assertFalse(item.input_schema["additionalProperties"])
            self.assertEqual(self.session.calls, [])

    async def test_catalogue_extra_missing_duplicate_schema_and_pagination_are_rejected(self):
        async with mcp_client(self.adapter) as client:
            good = await client.list_tools()
            variants = []
            for tools in (good.tools[:-1], good.tools + [good.tools[0]], [good.tools[0]] * 3):
                variants.append(good.model_copy(update={"tools": tools}))
            altered = deepcopy(good)
            altered.tools[1].input_schema["additionalProperties"] = True
            variants += [altered, good.model_copy(update={"next_cursor": "more"}),
                         good.model_copy(update={"result_type": "input_required"})]
            for bad in variants:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    binding.verify_catalogue(bad)

    async def test_exact_dispatch_and_unicode_arguments(self):
        async with mcp_client(self.adapter) as client:
            for name, args in (("lister", {}), ("lire", {"chemin": "entrees/fiche.md"}),
                               ("ecrire", {"chemin": "sorties/note.md", "contenu": "Été\n"})):
                result = await client.call_tool(name, args)
                self.assertFalse(result.is_error)
                self.assertTrue(payload(result)["ok"])
                self.assertEqual(self.session.calls[-1], (name, args))

    async def test_unknown_tools_extra_arguments_types_and_workspace_selection_cannot_dispatch(self):
        async with mcp_client(self.adapter) as client:
            for name, args in (("bash", {"command": "id"}), ("Read", {"file_path": "/etc/passwd"}),
                               ("lister", {"workspace": "/another"}),
                               ("lire", {"chemin": True}), ("lire", {}),
                               ("ecrire", {"chemin": "sorties/note.md", "contenu": "x", "run_id": "other"})):
                with self.subTest(name=name, args=args):
                    self.assertTrue((await client.call_tool(name, args)).is_error)
            self.assertEqual(self.session.calls, [])

    async def test_backend_refusal_is_an_mcp_error_without_retry(self):
        with patch.object(self.session, "call", return_value=dict(ok=False, code="chemin_refuse")) as call:
            async with mcp_client(self.adapter) as client:
                result = await client.call_tool("lire", {"chemin": "../private"})
                self.assertTrue(result.is_error)
                self.assertEqual(payload(result), dict(ok=False, code="chemin_refuse"))
                self.assertEqual(call.call_count, 1)

    async def test_host_exception_is_redacted_and_binding_stops(self):
        with patch.object(self.session, "call", side_effect=OSError("/private/HOST_SENTINEL/key")) as call:
            async with mcp_client(self.adapter) as client:
                result = await client.call_tool("lister", {})
                self.assertTrue(result.is_error)
                self.assertEqual(payload(result), dict(ok=False, code="erreur_io"))
                self.assertNotIn("HOST_SENTINEL", str(result))
                self.assertEqual(payload(await client.call_tool("lister", {}))["code"], "ferme")
            self.assertEqual(call.call_count, 1)

    async def test_fresh_options_disable_builtins_settings_plugins_and_session_reuse(self):
        options = self.adapter.options()
        self.adapter.verify_options(options)
        self.assertEqual(options.tools, [])
        self.assertEqual(options.setting_sources, [])
        self.assertTrue(options.strict_mcp_config)
        self.assertEqual(options.skills, [])
        self.assertEqual(options.plugins, [])
        self.assertIsNone(options.resume)
        self.assertIsNone(options.agents)
        self.assertEqual(list(Path(options.cwd).iterdir()), [])
        self.assertNotIn(str(ROOT), options.system_prompt)
        self.assertNotIn(str(ROOT), str(options.cwd))
        result = await options.can_use_tool("Bash", {}, None)
        self.assertEqual(result.behavior, "deny")

    async def test_options_overrides_are_rejected_including_inherited_context(self):
        changes = {"tools": ["Bash"], "allowed_tools": ["mcp__orka__*"], "strict_mcp_config": False,
                   "setting_sources": ["user"], "skills": "all", "plugins": [{"type": "local", "path": "/tmp"}],
                   "system_prompt": {"type": "preset", "preset": "claude_code"},
                   "cwd": str(ROOT), "env": {"ANTHROPIC_API_KEY": "fake"}, "resume": "old-session",
                   "continue_conversation": True, "permission_mode": "bypassPermissions",
                   "add_dirs": ["/tmp"], "agents": {}, "extra_args": {"tools": "default"}}
        for name, value in changes.items():
            options = self.adapter.options()
            setattr(options, name, value)
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.adapter.verify_options(options)
        options = self.adapter.options()
        options.mcp_servers["extra"] = {"type": "stdio", "command": "bash"}
        with self.assertRaises(ValueError):
            self.adapter.verify_options(options)
        options = self.adapter.options()
        options.mcp_servers["orka"]["instance"] = object()
        with self.assertRaises(ValueError):
            self.adapter.verify_options(options)
        self.adapter.verify_options(self.adapter.options())

    async def test_pinned_sdk_cli_argument_builder_keeps_the_restrictions_without_starting_cli(self):
        # Pinned SDK internal inspection only; never connect() or resolve/run a CLI.
        from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

        options = self.adapter.options()
        transport = SubprocessCLITransport(prompt="unused", options=options)
        transport._cli_path = "OFFLINE_CLI_NEVER_EXECUTED"
        command = transport._build_command()
        self.assertEqual(command[command.index("--tools") + 1], "")
        self.assertEqual(command[command.index("--allowedTools") + 1].split(","), list(binding.QUALIFIED))
        self.assertIn("--setting-sources=", command)
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--no-session-persistence", command)
        self.assertNotIn("--continue", command)
        self.assertEqual(json.loads(command[command.index("--mcp-config") + 1]),
                         {"mcpServers": {"orka": {"type": "sdk", "name": "orka"}}})

    async def test_closed_adapter_cannot_dispatch_or_prepare_options(self):
        async with mcp_client(self.adapter) as client:
            self.adapter.close()
            self.assertEqual(payload(await client.call_tool("lister", {}))["code"], "ferme")
            self.assertEqual(self.session.calls, [])
        with self.assertRaises(RuntimeError):
            self.adapter.options()

    async def test_backend_binding_mismatch_is_refused(self):
        self.session.record["contract_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            binding.ClaudeAdapter(self.session)


@unittest.skipUnless(os.environ.get("ORKA_CLAUDE_SDK") == "1" and os.environ.get("ORKA_P01_DOCKER") == "1",
                     "Opt-in Claude MCP to isolated Docker backend")
class DockerBindingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orka-claude-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = prepare(Path(self.tmp.name) / "first", "hostile")
        # The only permitted subprocess is the operator-owned Docker executable.
        real_popen = subprocess.Popen

        def docker_only(args, *positional, **kwargs):
            if type(args) is not list or args[0] != "docker" or kwargs.get("shell"):
                raise AssertionError("Only offline Docker allowed")
            return real_popen(args, *positional, **kwargs)

        for target, effect in (("subprocess.Popen", docker_only),
                               ("socket.socket.connect", AssertionError("No network")),
                               ("anyio.open_process", AssertionError("No Claude CLI")),
                               ("claude_agent_sdk.query", AssertionError("No model")),
                               ("claude_agent_sdk.ClaudeSDKClient.connect", AssertionError("No Claude client"))):
            guard = patch(target, side_effect=effect)
            guard.start()
            self.addCleanup(guard.stop)

    async def test_real_backend_isolation_over_mcp_and_confirmed_stop(self):
        sentinel = Path(self.tmp.name) / "private.md"
        sentinel.write_text("HOST_PRIVATE_SENTINEL", encoding="utf-8")
        with binding.open_adapter(self.root) as adapter:
            async with mcp_client(adapter) as client:
                listed = payload(await client.call_tool("lister", {}))
                self.assertTrue(listed["ok"])
                self.assertNotIn("controle/", str(listed))
                self.assertNotIn("cas.json", str(listed))
                hostile = payload(await client.call_tool("lire", {"chemin": "entrees/note.md"}))
                self.assertIn("Instruction hostile", hostile["donnees"]["contenu"])
                for path in (str(sentinel), "../private.md", "controle/cas.json", "entrees/../private.md"):
                    result = await client.call_tool("lire", {"chemin": path})
                    self.assertTrue(result.is_error)
                    self.assertEqual(payload(result)["code"], "chemin_refuse")
                    self.assertNotIn("HOST_PRIVATE_SENTINEL", str(result))
                source = await client.call_tool("ecrire", {"chemin": "entrees/note.md", "contenu": "bad"})
                self.assertEqual(payload(source)["code"], "chemin_refuse")
                args = {"chemin": "sorties/note.md", "contenu": "Été\n"}
                written = await client.call_tool("ecrire", args)
                self.assertFalse(written.is_error)
                self.assertEqual(payload(written)["donnees"]["sha256"], sha("Été\n".encode()))
                self.assertEqual(payload(await client.call_tool("ecrire", args))["code"], "existe")
                self.assertEqual(payload(await client.call_tool("lire", {"chemin": "sorties/note.md"}))["donnees"]["contenu"], "Été\n")
        self.assertFalse(decode((self.root / "controle/stopped.json").read_bytes())["state"]["Running"])
        self.assertEqual(sentinel.read_text(), "HOST_PRIVATE_SENTINEL")
        with self.assertRaises(FileExistsError):
            with binding.open_adapter(self.root):
                self.fail("No reset/retry")

    async def test_separate_runs_cannot_read_each_others_outputs(self):
        with binding.open_adapter(self.root) as first:
            first_id = first._session.run_id
            async with mcp_client(first) as client:
                await client.call_tool("ecrire", {"chemin": "sorties/note.md", "contenu": "FIRST_SENTINEL"})
        other = prepare(Path(self.tmp.name) / "second", "complet")
        with binding.open_adapter(other) as second:
            self.assertNotEqual(first_id, second._session.run_id)
            async with mcp_client(second) as client:
                self.assertEqual(payload(await client.call_tool("lire", {"chemin": "sorties/note.md"}))["code"], "absent")
                result = await client.call_tool("lire", {"chemin": "../first/outputs/sorties/note.md"})
                self.assertEqual(payload(result)["code"], "chemin_refuse")
                self.assertNotIn("FIRST_SENTINEL", str(result))

    async def test_links_inserted_after_start_cannot_escape_the_backend(self):
        target = self.root / "outputs/sorties/target.md"
        with binding.open_adapter(self.root) as adapter:
            # Deliberate operator-side tampering after worker startup. Neither
            # source nor output symlinks may bypass the existing openat2 checks.
            source = self.root / "inputs/entrees/note.md"
            source.chmod(0o600)
            original = source.read_bytes()
            target.write_bytes(original)
            source.unlink()
            source.symlink_to("/data/outputs/sorties/target.md")
            output = self.root / "outputs/sorties/note.md"
            output.symlink_to("/data/outputs/sorties/target.md")
            async with mcp_client(adapter) as client:
                result = await client.call_tool("lire", {"chemin": "entrees/note.md"})
                self.assertEqual(payload(result)["code"], "fichier_refuse")
                result = await client.call_tool("ecrire", {"chemin": "sorties/note.md", "contenu": "bad"})
                self.assertEqual(payload(result)["code"], "existe")
                self.assertEqual(target.read_bytes(), original)

    async def test_backend_call_quota_still_closes_without_retry(self):
        with binding.open_adapter(self.root) as adapter:
            async with mcp_client(adapter) as client:
                for _ in range(24):
                    self.assertFalse((await client.call_tool("lister", {})).is_error)
                result = await client.call_tool("lister", {})
                self.assertTrue(result.is_error)
                self.assertEqual(payload(result)["code"], "quota")
        events = (self.root / "controle/events.jsonl").read_bytes().splitlines()
        self.assertEqual(len(events), 25)


if __name__ == "__main__":
    unittest.main()
