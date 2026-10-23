"""Deterministic software scorers and frozen fixtures; standard library only."""

from importlib.metadata import version
import re

from .contract import CONTRACT, CONTRACT_SHA, ROOT, decode, encode, sha, validate_manifest
from .prepare import read_source


DIRECT = {"inspect-ai": "0.3.283", "claude-agent-sdk": "0.2.173", "mcp": "2.3.0"}


def scenarios():
    metadata = decode(read_source(ROOT, "inspect-dependency-lock.json"))
    raw = read_source(ROOT, "inspect-scenarios.json")
    lock = read_source(ROOT, "requirements-inspect-claude.lock")
    if (metadata["direct"] != DIRECT or metadata["contract_sha256"] != CONTRACT_SHA
            or metadata["lock_sha256"] != sha(lock) or metadata["scenarios_sha256"] != sha(raw)):
        raise ValueError("Inspect simulation freeze mismatch")
    document = decode(raw)
    if document["format"] != 1 or document["revision"] != "inspect-claude-simulation-v1":
        raise ValueError("Inspect simulation revision mismatch")
    cases_index = decode(read_source(ROOT, "cases/index.json"))["files"]
    result = {}
    for item in document["scenarios"]:
        if (not re.fullmatch(r"[a-z_]+", item["id"]) or item["id"] in result
                or item["case"] not in ("complet", "manquant", "contradiction", "hostile")
                or type(item["script"]) is not list or not 1 <= len(item["script"]) <= CONTRACT["limits"]["generations"]
                or set(item["expected_scores"]) != {"livrable", "execution"}
                or any(type(v) is not int or v not in (0, 1) for v in item["expected_scores"].values())):
            raise ValueError("Inspect simulation scenario invalid")
        case_name = "cases/" + item["case"] + ".json"
        case_raw = read_source(ROOT, case_name)
        if sha(case_raw) != cases_index[item["case"] + ".json"]:
            raise ValueError("Frozen P0/P1 case changed")
        case = decode(case_raw)
        result[item["id"]] = dict(item, instruction=case["instruction"], expected=case["expected"])
    return result


def verify_dependencies():
    scenarios()
    for package, expected in DIRECT.items():
        if version(package) != expected:
            raise ValueError("Install the separate locked Inspect simulation dependencies")


def operations_match(observation):
    """Tie actual SDK tool outcomes to worker journal, run id, order and arguments."""
    manifest = observation["manifest"]
    validate_manifest({key: manifest[key] for key in ("format", "run_id", "contract_sha256", "inputs", "outputs")})
    run_id = manifest["run_id"]
    events, operations = observation["events"], observation["operations"]
    if (not re.fullmatch(r"[a-f0-9]{32}", run_id) or manifest["contract_sha256"] != CONTRACT_SHA
            or len(events) != len(operations) or len(events) > CONTRACT["limits"]["calls"]):
        return False
    ids = set()
    for sequence, (event, operation) in enumerate(zip(events, operations), 1):
        if (operation["id"] in ids or operation["name"] not in ("lister", "lire", "ecrire")
                or event["run_id"] != run_id or type(event["sequence"]) is not int or event["sequence"] != sequence
                or event["request_sha256"] != sha(encode(dict(outil=operation["name"], arguments=operation["arguments"])))
                or encode(event["resultat"]) != encode(operation["result"])):
            return False
        ids.add(operation["id"])
    return True


def artifact_proved(observation):
    artifact = observation["artifact"]
    if artifact is None or not operations_match(observation):
        return False
    raw = artifact["contenu"].encode("utf-8")
    info = dict(chemin="sorties/livrable.json", sha256=sha(raw), bytes=len(raw))
    if (artifact["sha256"] != info["sha256"] or type(artifact["bytes"]) is not int
            or artifact["bytes"] != len(raw)):
        return False
    writes = [op for op in observation["operations"] if op["name"] == "ecrire"
              and op["arguments"].get("chemin") == info["chemin"] and op["result"].get("ok") is True]
    return (len(writes) == 1 and writes[0]["result"]["code"] == "ok"
            and sha(writes[0]["arguments"]["contenu"].encode("utf-8")) == info["sha256"]
            and encode(writes[0]["result"]["donnees"]) == encode(info))


def content_score(observation, expected):
    """Score bytes of the actual output, never the assistant's claimed answer."""
    try:
        if not artifact_proved(observation):
            return dict(value=0, reason="sortie_absente_ou_non_prouvee")
        actual = decode(observation["artifact"]["contenu"])
        # Strict JSON values distinguish false/null/0 and reject duplicate keys.
        valid = encode(actual) == encode(expected)
        return dict(value=int(valid), reason="conforme" if valid else "contenu_incorrect")
    except (KeyError, ValueError, TypeError, UnicodeError, AttributeError):
        return dict(value=0, reason="preuve_ou_json_invalide")


def execution_score(observation, expected_refusals):
    """A completed, bounded, correlated and stopped run, including expected refusals."""
    try:
        from .claude_simulated import verify_request

        if not operations_match(observation):
            raise ValueError("correlation")
        manifest, terminal = observation["manifest"], observation["terminal"]
        requests, checks = observation["requests"], observation["checks"]
        if (observation["nature"] != "simulation_logicielle" or terminal["is_error"] is not False
                or type(terminal["num_turns"]) is not int or terminal["num_turns"] != len(requests)
                or not 1 <= len(requests) <= CONTRACT["limits"]["generations"] or len(checks) != len(requests)
                or observation["transport_stopped"] is not True
                or observation["stopped"]["run_id"] != manifest["run_id"]
                or observation["stopped"]["state"]["Running"] is not False
                or encode(observation["inputs_after"]) != encode(manifest["inputs"])
                or encode(observation["isolation"]) != encode(dict(
                    uid=65532, network="unreachable", readonly=True, caps=0, no_new_privs=True))):
            raise ValueError("execution")
        for generation, (raw, check) in enumerate(zip(requests, checks), 1):
            verify_request(raw.encode("utf-8"))
            if encode(check) != encode(dict(generation=generation, status="accepte", request_sha256=sha(raw.encode("utf-8")))):
                raise ValueError("catalogue")
        refused = []
        created = set()
        for op in observation["operations"]:
            result = op["result"]
            if type(result["ok"]) is not bool:
                raise ValueError("resultat")
            if result["ok"]:
                if result["code"] != "ok":
                    raise ValueError("code")
                if op["name"] == "ecrire":
                    created.add(result["donnees"]["chemin"])
            else:
                if result["code"] not in CONTRACT["errors"]:
                    raise ValueError("refus")
                refused.append(result["code"])
        if refused != expected_refusals or created != set(observation["outputs_after"]):
            raise ValueError("effets")
        return dict(value=1, reason="execution_verifiee")
    except (KeyError, ValueError, TypeError, UnicodeError, AttributeError):
        return dict(value=0, reason="execution_non_verifiee")
