#!/usr/bin/env python3
"""Optional tools-only MCP stdio bridge. Never starts a model or writes host settings."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


MAX_MESSAGE = 1024 * 1024
PROTOCOLS = ("2025-11-25", "2025-06-18")
FIELDS = {"lister": (), "lire": ("chemin",), "ecrire": ("chemin", "contenu")}


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")


def error(identifier, code, message):
    return {"jsonrpc": "2.0", "id": identifier, "error": {"code": code, "message": message}}


class Bridge:
    def __init__(self, adapter, fingerprint, execution):
        self.adapter = Path(adapter).absolute()
        self.fingerprint = fingerprint
        self.execution = execution
        self.state = "new"
        self.verify_adapter()

    def verify_adapter(self):
        if self.adapter.is_symlink() or not self.adapter.is_file():
            raise ValueError("A regular operator-owned adapter is required")
        if hashlib.sha256(self.adapter.read_bytes()).hexdigest() != self.fingerprint:
            raise ValueError("Adapter fingerprint mismatch")

    def call(self, name, arguments):
        keys = FIELDS[name]
        if type(arguments) is not dict or set(arguments) != set(keys) or any(type(v) is not str for v in arguments.values()):
            return {"content": [{"type": "text", "text": "Arguments refusés"}], "isError": True}
        try:
            self.verify_adapter()
            result = subprocess.run(
                [sys.executable, "-I", "-X", "utf8", "-B", str(self.adapter), "--execution", self.execution],
                input=encode({"action": name, **arguments}), capture_output=True, timeout=35)
            if len(result.stdout) > 4 * MAX_MESSAGE or result.returncode not in (0, 2):
                raise ValueError("Invalid adapter result")
            data = decode(result.stdout)
            if type(data) is not dict or type(data.get("ok")) is not bool or (result.returncode == 0) != data["ok"]:
                raise ValueError("Invalid adapter status")
            return {"content": [{"type": "text", "text": encode(data).decode("utf-8")}], "isError": not data["ok"]}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"content": [{"type": "text", "text": "Adaptateur indisponible ou refusé"}], "isError": True}

    def handle(self, message):
        if type(message) is not dict or message.get("jsonrpc") != "2.0" or type(message.get("method")) is not str:
            return error(None, -32600, "Invalid request")
        identifier = message.get("id")
        if "id" in message and type(identifier) not in (int, str):
            return error(None, -32600, "Invalid request id")
        method, params = message["method"], message.get("params", {})
        if "id" not in message:
            if method == "notifications/initialized" and self.state == "initializing":
                self.state = "ready"
            return None  # Notifications never execute a tool or receive a response.
        if type(params) is not dict:
            return error(identifier, -32602, "Object parameters required")
        if method == "initialize":
            if self.state != "new":
                return error(identifier, -32600, "Already initialized")
            if (type(params.get("protocolVersion")) is not str or type(params.get("capabilities")) is not dict
                    or type(params.get("clientInfo")) is not dict
                    or any(type(params["clientInfo"].get(k)) is not str for k in ("name", "version"))):
                return error(identifier, -32602, "Initialization fields required")
            self.state = "initializing"
            value = {"protocolVersion": params["protocolVersion"] if params["protocolVersion"] in PROTOCOLS else PROTOCOLS[0],
                     "capabilities": {"tools": {}}, "serverInfo": {"name": "orka-files", "version": "0.1.0"}}
        elif method == "ping":
            value = {}
        elif self.state != "ready":
            return error(identifier, -32600, "Initialize first")
        elif method == "tools/list":
            if params:
                return error(identifier, -32602, "No pagination or extra parameters")
            value = {"tools": [{"name": name, "description": description,
                                "inputSchema": {"type": "object", "properties": {k: {"type": "string"} for k in FIELDS[name]},
                                                "required": list(FIELDS[name]), "additionalProperties": False},
                                "annotations": {"readOnlyHint": name != "ecrire", "openWorldHint": False}}
                               for name, description in (("lister", "Lister les fichiers autorisés"),
                                                         ("lire", "Lire un fichier autorisé"),
                                                         ("ecrire", "Écrire un livrable autorisé"))]}
        elif method == "tools/call":
            if (not set(params) <= {"name", "arguments", "_meta"} or type(params.get("name")) is not str
                    or params["name"] not in FIELDS):
                return error(identifier, -32602, "Unknown tool or extra parameters")
            value = self.call(params["name"], params.get("arguments", {}))
        else:
            return error(identifier, -32601, "Method not supported")
        return {"jsonrpc": "2.0", "id": identifier, "result": value}


def serve(bridge, source, destination):
    while True:
        raw = source.readline(MAX_MESSAGE + 2)
        if not raw:
            return
        if len(raw) > MAX_MESSAGE:
            destination.write(encode(error(None, -32600, "Message too large")) + b"\n")
            destination.flush()
            return  # Do not interpret the rest of an oversized frame as a new request.
        try:
            result = bridge.handle(decode(raw))
        except (ValueError, UnicodeError, RecursionError):
            result = error(None, -32700, "Invalid JSON")
        if result is not None:
            destination.write(encode(result) + b"\n")
            destination.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, type=Path)
    parser.add_argument("--empreinte-adaptateur", required=True)
    parser.add_argument("--execution", required=True)
    args = parser.parse_args()
    try:
        bridge = Bridge(args.adapter, args.empreinte_adaptateur, args.execution)
        serve(bridge, sys.stdin.buffer, sys.stdout.buffer)
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
