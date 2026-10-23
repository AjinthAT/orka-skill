"""Optional Inspect task and offline runner for the scripted Claude transport."""

import argparse
import asyncio
from contextlib import ExitStack, contextmanager
from pathlib import Path
import subprocess
from unittest.mock import patch

from inspect_ai import Task, eval_async
from inspect_ai.dataset import Sample
from inspect_ai.model import ModelOutput
from inspect_ai.scorer import Score, mean, scorer
from inspect_ai.solver import solver

from .claude_adapter import NAMES, QUALIFIED, open_adapter
from .claude_simulated import MODEL, simulated_client
from .contract import ROOT, decode, encode, sha
from .inspect_scoring import content_score, execution_score, scenarios, verify_dependencies
from .prepare import prepare, read_source, save


@contextmanager
def offline_only():
    """Scoped process-wide guards; run this harness in its own Python process."""
    real_popen = subprocess.Popen

    def docker_only(args, *positional, **kwargs):
        if type(args) is not list or args[0] != "docker" or kwargs.get("shell"):
            raise RuntimeError("Offline harness permits only its Docker file worker")
        return real_popen(args, *positional, **kwargs)

    with ExitStack() as stack:
        generation = stack.enter_context(patch("inspect_ai.model.Model.generate", side_effect=RuntimeError("Generation forbidden")))
        # This pinned Inspect hook otherwise spawns git for optional log metadata.
        # Our provenance records exact source hashes instead; no revision is invented.
        stack.enter_context(patch("inspect_ai._eval.task.log.resolve_revision", return_value=None))
        for target in ("socket.socket.connect", "socket.socket.connect_ex", "anyio.open_process",
                       "asyncio.create_subprocess_exec", "claude_agent_sdk.query",
                       "claude_agent_sdk._internal.transport.subprocess_cli.SubprocessCLITransport.__init__"):
            stack.enter_context(patch(target, side_effect=RuntimeError("Offline simulation only")))
        stack.enter_context(patch("subprocess.Popen", side_effect=docker_only))
        yield generation


def tool_operations(messages):
    """Correlate SDK assistant tool uses and actual SDK tool results, without a judge."""
    from claude_agent_sdk import AssistantMessage, ToolResultBlock, ToolUseBlock, UserMessage

    pending, result = {}, []
    for message in messages:
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    if block.id in pending or block.name not in QUALIFIED:
                        raise ValueError("Uncorrelated SDK operation")
                    pending[block.id] = dict(id=block.id, name=NAMES[QUALIFIED.index(block.name)], arguments=block.input)
        elif isinstance(message, UserMessage) and isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    operation = pending.pop(block.tool_use_id)
                    try:
                        value = decode(block.content[0]["text"])
                    except (ValueError, KeyError, TypeError, IndexError):
                        value = dict(ok=False, code="protocole_mcp_invalide")
                    result.append(dict(operation, result=value))
    if pending:
        raise ValueError("SDK tool did not finish")
    return result


def capture(root, transport, messages):
    manifest = decode(read_source(root, "controle/manifest.json"))
    fingerprints = {}
    for name in manifest["inputs"]:
        raw = read_source(root / "inputs", name)
        fingerprints[name] = dict(bytes=len(raw), sha256=sha(raw))
    artifact = None
    path = "sorties/livrable.json"
    try:
        raw = read_source(root / "outputs", path)
        artifact = dict(contenu=raw.decode("utf-8"), bytes=len(raw), sha256=sha(raw))
    except FileNotFoundError:
        pass
    terminal = messages[-1]
    observation = dict(
        nature="simulation_logicielle", manifest=manifest,
        terminal=dict(is_error=terminal.is_error, num_turns=terminal.num_turns, result=terminal.result),
        transport_stopped=not transport.is_ready() and transport._task.done(),
        requests=[raw.decode("utf-8") for raw in transport.requests], checks=transport.checks,
        operations=tool_operations(messages), artifact=artifact, inputs_after=fingerprints,
        outputs_after=sorted(p.relative_to(root / "outputs").as_posix()
                             for p in (root / "outputs").rglob("*") if not p.is_dir()),
        events=[decode(raw) for raw in (root / "controle/events.jsonl").read_bytes().splitlines()]
               if (root / "controle/events.jsonl").exists() else [],
        isolation=decode(read_source(root, "controle/isolation.json")),
        stopped=decode(read_source(root, "controle/stopped.json")),
    )
    save(root / "controle/inspect-observation.json", encode(observation), 0o600)
    return observation


@solver
def claude_scripted(destination: str):
    async def solve(state, generate):
        # Inspect's Generate callable is deliberately never used.
        selected = scenarios()[str(state.sample_id)]
        root = prepare(Path(destination) / "runs" / selected["id"], selected["case"])
        with open_adapter(root) as adapter:
            async with simulated_client(adapter, selected["script"]) as (client, transport):
                await client.query(state.input_text)
                messages = [message async for message in client.receive_response()]
        observation = capture(root, transport, messages)  # Only after confirmed writer stop.
        state.store.set("orka_observation", observation)
        state.output = ModelOutput.from_content(model=MODEL, content=messages[-1].result or "Simulation logicielle")
        state.completed = True
        return state

    return solve


@scorer(metrics=[mean()])
def livrable():
    async def score(state, target):
        verdict = content_score(state.store.get("orka_observation", {}), decode(target.text))
        return Score(value=verdict["value"], explanation=verdict["reason"])
    return score


@scorer(metrics=[mean()])
def execution():
    async def score(state, target):
        selected = scenarios()[str(state.sample_id)]
        verdict = execution_score(state.store.get("orka_observation", {}), selected["expected_refusals"])
        return Score(value=verdict["value"], explanation=verdict["reason"])
    return score


def task(destination, scenario_ids=None):
    verify_dependencies()
    choices = scenarios()
    ids = list(choices) if scenario_ids is None else list(scenario_ids)
    if not ids or len(set(ids)) != len(ids) or any(name not in choices for name in ids):
        raise ValueError("Select unique frozen scenario ids")
    samples = [Sample(id=name, input=choices[name]["instruction"], target=encode(choices[name]["expected"]).decode(),
                      metadata=dict(nature="simulation_logicielle", case=choices[name]["case"])) for name in ids]
    return Task(name="orka_claude_simulation", version="1", dataset=samples,
                solver=claude_scripted(str(destination)), scorer=[livrable(), execution()],
                model="mockllm/model", epochs=1, fail_on_error=True,
                metadata=dict(nature="simulation_logicielle", real_model_calls="forbidden"))


async def run(destination, scenario_ids=None):
    verify_dependencies()
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Existing evaluation preserved; choose a new destination")
    root = destination.parent.resolve(strict=True) / destination.name
    selected_task = task(root, scenario_ids)
    root.mkdir(mode=0o700)
    (root / "runs").mkdir()
    (root / "logs").mkdir()
    sources = ("inspect_simulated.py", "inspect_scoring.py", "claude_adapter.py", "claude_simulated.py",
               "prepare.py", "container.py", "backend.py", "contract.py", "contract.json",
               "inspect-scenarios.json", "inspect-dependency-lock.json", "requirements-inspect-claude.lock")
    save(root / "provenance.json", encode(dict(nature="simulation_logicielle",
         files={name: sha((ROOT / name).read_bytes()) for name in sources})), 0o600)
    with offline_only() as generation:
        logs = await eval_async(selected_task, model="mockllm/model", max_samples=1, max_tasks=1, epochs=1,
                                retry_on_error=0, log_dir=str(root / "logs"), log_format="json", log_shared=False,
                                log_realtime=False, log_model_api=False, score_display=False, notification=False,
                                ctl_server=False, acp_server=False)
    choices = scenarios()
    actual = {str(sample.id): {name: score.value for name, score in sample.scores.items()}
              for sample in (logs[0].samples or []) if sample.scores}
    expected = {str(sample.id): choices[str(sample.id)]["expected_scores"] for sample in selected_task.dataset}
    receipt = dict(nature="simulation_logicielle", inspect_status=logs[0].status,
                   model_generate_attempts=generation.call_count, scores=actual, expected_scores=expected,
                   matrix_matches=actual == expected, model_usage=logs[0].stats.model_usage)
    save(root / "reception.json", encode(receipt), 0o600)
    if logs[0].status != "success" or generation.call_count or receipt["model_usage"] or actual != expected:
        raise RuntimeError("Inspect simulation did not meet its frozen software acceptance matrix")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = asyncio.run(run(args.destination))
        print(encode(receipt).decode())
    except (OSError, ValueError, RuntimeError):
        parser.exit(2, "Offline Inspect evaluation refused; preserve any existing evidence\n")


if __name__ == "__main__":
    main()
