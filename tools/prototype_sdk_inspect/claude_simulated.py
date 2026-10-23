"""Offline Claude control-protocol transport; scripted replies, never a provider."""

import asyncio
from contextlib import asynccontextmanager
import time

from .claude_adapter import (
    DESCRIPTIONS, NAMES, QUALIFIED, SERVER, SYSTEM_PROMPT, verify_catalogue, verify_dependencies,
)
from .contract import CONTRACT_BYTES, decode, encode, sha


SPEC = decode(CONTRACT_BYTES)
MODEL = "orka-offline-simulation"


class SimulationRefused(ValueError):
    pass


def request_tools():
    """Independent frozen authority, not the SDK's mutable tools/list objects."""
    return [{"name": qualified, "description": DESCRIPTIONS[item["name"]],
             "input_schema": item["parameters"]}
            for qualified, item in zip(QUALIFIED, decode(CONTRACT_BYTES)["tools"])]


def verify_request(raw):
    """Last boundary before a scripted reply is consumed; no I/O or callbacks."""
    request = decode(raw)
    expected = {"model", "system", "messages", "tools"}
    if (type(request) is not dict or set(request) != expected or request["model"] != MODEL
            or request["system"] != SYSTEM_PROMPT or type(request["messages"]) is not list
            or not request["messages"] or type(request["tools"]) is not list
            or len(request["tools"]) != 3
            or sorted((encode(item) for item in request["tools"]))
            != sorted(encode(item) for item in request_tools())):
        raise SimulationRefused("catalogue_refuse")


class SimulatedClaudeTransport:
    """Implements the pinned SDK Transport interface, using only memory queues.

    The SDK routes our mcp_message control requests to its real in-process server.
    Each simulated generation re-reads tools/list and checks the serialized final
    catalogue. No CLI, socket, arbitrary sender or provider callback exists here.
    One user query per transport; generations and deadline never reset.
    """

    def __init__(self, adapter, options, script):
        verify_dependencies()
        adapter.verify_options(options)
        if type(script) is not list or not script or len(encode(script)) > SPEC["limits"]["request_bytes"]:
            raise SimulationRefused("script_refuse")
        self._script = decode(encode(script))
        self._adapter, self._options = adapter, options
        self._queue = asyncio.Queue()
        self._pending = {}
        self._abandoned = set()
        self._task = None
        self._ready = self._closed = self._failed = self._initialized = self._used = False
        self._input_ended = False
        self._sequence = 0
        self._requests = []
        self._checks = []

    @property
    def requests(self):
        return tuple(self._requests)  # Immutable byte snapshots, no shared mutable catalogue.

    @property
    def checks(self):
        return decode(encode(self._checks))

    async def connect(self):
        if self._closed or self._ready:
            raise SimulationRefused("transport_non_reutilisable")
        self._adapter.verify_options(self._options)
        self._started = time.monotonic()
        self._deadline = self._started + SPEC["limits"]["seconds"]
        self._ready = True

    def is_ready(self):
        return self._ready and not self._closed and not self._failed

    async def write(self, data):
        if self._closed or not self._ready or type(data) is not str:
            raise SimulationRefused("transport_ferme")
        try:
            # Exactly one NDJSON frame, duplicate keys refused by the shared decoder.
            raw = data.removesuffix("\n")
            if "\n" in raw or "\r" in raw or len(raw.encode()) > SPEC["limits"]["request_bytes"]:
                raise SimulationRefused("protocole_refuse")
            frame = decode(raw)
            if type(frame) is not dict:
                raise SimulationRefused("protocole_refuse")
            if frame.get("type") == "control_response":
                response = frame["response"]
                request_id = response["request_id"]
                if request_id in self._abandoned:
                    return  # Late reply to a timed-out request cannot resume the run.
                future = self._pending[request_id]
                if future.done():
                    raise SimulationRefused("correlation_refusee")
                if response["subtype"] == "success":
                    future.set_result(response["response"]["mcp_response"])
                else:
                    future.set_exception(SimulationRefused("mcp_refuse"))
                return
            if self._failed:
                raise SimulationRefused("transport_ferme")
            if frame.get("type") == "control_request" and not self._initialized:
                if frame["request"] != {"subtype": "initialize", "hooks": None, "skills": []}:
                    raise SimulationRefused("initialisation_refusee")
                self._adapter.verify_options(self._options)
                self._initialized = True
                self._queue.put_nowait(dict(type="control_response", response=dict(
                    subtype="success", request_id=frame["request_id"], response={})))
                return
            if (frame.get("type") != "user" or not self._initialized or self._used or self._input_ended
                    or frame.get("parent_tool_use_id") is not None
                    or frame["message"]["role"] != "user" or type(frame["message"]["content"]) is not str):
                raise SimulationRefused("protocole_refuse")
            self._used = True
            self._task = asyncio.create_task(self._run(frame["message"]["content"]))
        except (ValueError, KeyError, TypeError):
            self._failed = True
            raise SimulationRefused("protocole_refuse") from None

    async def _rpc(self, method, params=None, notification=False):
        self._sequence += 1
        request_id = "simulation-" + str(self._sequence)
        message = dict(jsonrpc="2.0", method=method)
        if not notification:
            message["id"] = self._sequence
        if params is not None:
            message["params"] = params
        future = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        self._queue.put_nowait(dict(type="control_request", request_id=request_id,
                                   request=dict(subtype="mcp_message", server_name=SERVER, message=message)))
        try:
            timeout = min(SPEC["limits"]["operation_seconds"], max(0, self._deadline - time.monotonic()))
            response = await asyncio.wait_for(future, timeout)
            if (response.get("jsonrpc") != "2.0" or "error" in response or "result" not in response
                    or (not notification and response.get("id") != message["id"])):
                raise SimulationRefused("mcp_refuse")
            return response["result"]
        finally:
            self._pending.pop(request_id, None)
            if future.cancelled():
                self._abandoned.add(request_id)

    def _build_request(self, catalogue, history):
        return dict(model=MODEL, system=SYSTEM_PROMPT, messages=decode(encode(history)),
                    tools=[dict(name="mcp__" + SERVER + "__" + tool.name,
                                description=tool.description, input_schema=tool.input_schema)
                           for tool in catalogue.tools])

    def _complete(self, raw, reply):
        # Nothing may be injected between this check and the local script sink.
        if len(self._requests) >= SPEC["limits"]["generations"] or time.monotonic() >= self._deadline:
            raise SimulationRefused("quota")
        verify_request(raw)
        self._requests.append(raw)
        return decode(encode(reply))

    def _emit(self, role, content):
        message = dict(role=role, content=content)
        if role == "assistant":
            message["model"] = MODEL
        self._queue.put_nowait(dict(type=role, message=message, parent_tool_use_id=None))

    def _result(self, code):
        self._queue.put_nowait(dict(type="result", subtype="success" if code == "ok" else "error_during_execution",
                                   duration_ms=int((time.monotonic() - self._started) * 1000),
                                   duration_api_ms=0, is_error=code != "ok",
                                   num_turns=len(self._requests), session_id="simulation-only",
                                   result="Simulation logicielle" if code == "ok" else code))

    async def _run(self, prompt):
        from mcp.types import LATEST_PROTOCOL_VERSION, ListToolsResult

        history = [dict(role="user", content=prompt)]
        generation = 1
        try:
            await self._rpc("initialize", dict(protocolVersion=LATEST_PROTOCOL_VERSION, capabilities={},
                                               clientInfo=dict(name="orka-simulation", version="1")))
            await self._rpc("notifications/initialized", notification=True)
            for reply in self._script:
                generation = len(self._requests) + 1
                if len(self._requests) >= SPEC["limits"]["generations"] or time.monotonic() >= self._deadline:
                    raise SimulationRefused("quota")
                self._adapter.verify_options(self._options)
                catalogue = ListToolsResult.model_validate(await self._rpc("tools/list"))
                verify_catalogue(catalogue)
                raw = encode(self._build_request(catalogue, history))
                self._adapter.verify_options(self._options)
                response = self._complete(raw, reply)
                self._checks.append(dict(generation=len(self._requests), request_sha256=sha(raw), status="accepte"))
                if type(response) is dict and set(response) == {"text"} and type(response["text"]) is str:
                    self._emit("assistant", [dict(type="text", text=response["text"])])
                    self._result("ok")
                    return
                if (type(response) is not dict or set(response) != {"tool", "arguments"}
                        or response["tool"] not in QUALIFIED or type(response["arguments"]) is not dict):
                    raise SimulationRefused("reponse_refusee")
                tool_id = "tool-simulation-" + str(len(self._requests))
                block = dict(type="tool_use", id=tool_id, name=response["tool"], input=response["arguments"])
                self._emit("assistant", [block])
                history.append(dict(role="assistant", content=[block]))
                # Recheck after emitting the fictitious response, before any file operation.
                self._adapter.verify_options(self._options)
                result = await self._rpc("tools/call", dict(name=NAMES[QUALIFIED.index(response["tool"])],
                                                           arguments=response["arguments"]))
                block = dict(type="tool_result", tool_use_id=tool_id,
                             content=result["content"], is_error=result.get("isError", False))
                self._emit("user", [block])
                history.append(dict(role="user", content=[block]))
            raise SimulationRefused("script_epuise")
        except Exception as error:
            self._failed = True
            code = str(error) if isinstance(error, SimulationRefused) else "simulation_refusee"
            self._checks.append(dict(generation=generation, status="refuse", code=code))
            self._result(code)

    async def read_messages(self):
        while True:
            frame = await self._queue.get()
            if frame is None:
                return
            yield frame

    async def end_input(self):
        self._input_ended = True

    async def close(self):
        if self._closed:
            return
        self._closed = True
        self._ready = False
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, 1)
            except (asyncio.CancelledError, TimeoutError):
                pass
        self._queue.put_nowait(None)


@asynccontextmanager
async def simulated_client(adapter, script):
    """Real SDK client with mandatory local transport, never a default fallback."""
    from claude_agent_sdk import ClaudeSDKClient

    options = adapter.options()
    transport = SimulatedClaudeTransport(adapter, options, script)
    async with ClaudeSDKClient(options=options, transport=transport) as client:
        yield client, transport
