"""Versioned contract and strict JSON; standard library only."""

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


CONTRACT_BYTES = (ROOT / "contract.json").read_bytes()
CONTRACT = decode(CONTRACT_BYTES)
CONTRACT_SHA = sha(CONTRACT_BYTES)


def logical(value, prefix=None):
    if (type(value) is not str or len(value) > 200
            or not re.fullmatch(r"[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_.-]+)+", value)
            or any(part in (".", "..") for part in value.split("/"))
            or (prefix is not None and not value.startswith(prefix + "/"))):
        raise ValueError("Invalid logical path")
    return value


def validate_manifest(value):
    if (type(value) is not dict or set(value) != {"format", "run_id", "contract_sha256", "inputs", "outputs"}
            or type(value["format"]) is not int or value["format"] != 1
            or value["contract_sha256"] != CONTRACT_SHA
            or type(value["run_id"]) is not str or not re.fullmatch(r"[0-9a-f]{32}", value["run_id"])
            or type(value["inputs"]) is not dict or type(value["outputs"]) is not list
            or not value["inputs"] or not value["outputs"]
            or len(value["inputs"]) + len(value["outputs"]) > CONTRACT["limits"]["inventory"]):
        raise ValueError("Invalid backend manifest")
    for name, info in value["inputs"].items():
        logical(name)
        if name.split("/")[0] not in ("entrees", "instructions"):
            raise ValueError("Invalid input namespace")
        if (type(info) is not dict or set(info) != {"sha256", "bytes"}
                or type(info["bytes"]) is not int or not 0 <= info["bytes"] <= CONTRACT["limits"]["read_bytes"]
                or type(info["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", info["sha256"])):
            raise ValueError("Invalid input fingerprint")
    for name in value["outputs"]:
        logical(name, "sorties")
    if len(set(value["outputs"])) != len(value["outputs"]):
        raise ValueError("Duplicate output")
    names = sorted([*value["inputs"], *value["outputs"]])
    if any(b.startswith(a + "/") for a, b in zip(names, names[1:])):
        raise ValueError("File/directory collision")
    return value
