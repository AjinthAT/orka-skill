"""Freeze a new P01 fixture. Never imports SDKs, starts Docker or calls a model."""

import argparse
import os
from pathlib import Path
import shutil
import stat
import sys
import uuid

from .contract import CONTRACT, CONTRACT_BYTES, CONTRACT_SHA, ROOT, decode, encode, logical, sha, validate_manifest


def read_source(root, name):
    """Read only ordinary single-link files from the explicitly trusted source tree."""
    if (type(name) is not str or Path(name).is_absolute() or "\\" in name or "\0" in name
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("Relative source path required")
    current = root
    for part in Path(name).parts:
        current = current / part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Source link refused")
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Ordinary single-link source required")
    fd = os.open(current, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("Source changed")
        raw = stream.read(CONTRACT["limits"]["read_bytes"] + 1)
    if len(raw) > CONTRACT["limits"]["read_bytes"]:
        raise ValueError("Source too large")
    raw.decode("utf-8")
    return raw


def save(path, raw, mode=0o444):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
    path.chmod(mode)


def prepare(destination, case):
    if case not in ("complet", "manquant", "contradiction", "hostile"):
        raise ValueError("Unknown independent case")
    destination = Path(destination).absolute()
    if os.path.lexists(destination):
        raise FileExistsError("Existing destination preserved")
    # The operator chooses/resolves the parent explicitly; nothing is merged.
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    fixture_raw = read_source(ROOT, "cases/" + case + ".json")
    cases_raw = read_source(ROOT, "cases/index.json")
    cases = decode(cases_raw)
    if cases["format"] != 1 or cases["files"][case + ".json"] != sha(fixture_raw):
        raise ValueError("Frozen case changed; use an explicit new revision")
    fixture = decode(fixture_raw)
    source = ROOT.parents[1] / ".agents/skills/orka"
    inputs = dict(fixture["inputs"])
    for name, original in (("instructions/SKILL.md", "SKILL.md"),
                           ("instructions/prompting-agents.md", "references/prompting-agents.md")):
        inputs[name] = read_source(source, original).decode("utf-8")
    inputs["instructions/tache.txt"] = fixture["instruction"]
    contents = {logical(name): text.encode("utf-8") for name, text in inputs.items()}
    manifest = dict(format=1, run_id=uuid.uuid4().hex, contract_sha256=CONTRACT_SHA,
                    inputs={name: dict(sha256=sha(raw), bytes=len(raw)) for name, raw in contents.items()},
                    outputs=["sorties/livrable.json", "sorties/livrable-v2.json", "sorties/note.md"])
    validate_manifest(manifest)
    runtime = {name: read_source(ROOT, name) for name in ("backend.py", "contract.py")}
    runtime["contract.json"] = CONTRACT_BYTES
    runtime["backend-manifest.json"] = encode(manifest)
    lock = read_source(ROOT, "requirements.lock")
    dependency_raw = read_source(ROOT, "dependency-lock.json")
    dependency = decode(dependency_raw)
    if dependency["lock_sha256"] != sha(lock) or dependency["contract_sha256"] != CONTRACT_SHA:
        raise ValueError("Dependency lock changed; freeze a new contract revision")
    destination.mkdir(mode=0o700)
    try:
        for name, raw in contents.items():
            save(destination / "inputs" / name, raw)
        (destination / "outputs/sorties").mkdir(parents=True)
        # Parent workspace is 0700; the isolated uid needs access to its sole output mount.
        (destination / "outputs").chmod(0o777)
        (destination / "outputs/sorties").chmod(0o777)
        for name, raw in runtime.items():
            save(destination / "runtime" / name, raw)
        save(destination / "controle/cas.json", fixture_raw)
        save(destination / "controle/cases-index.json", cases_raw)
        save(destination / "controle/requirements.lock", lock)
        save(destination / "controle/dependency-lock.json", dependency_raw)
        record = dict(format=1, nature="simulation_logicielle", case=case, run_id=manifest["run_id"],
                      contract_sha256=CONTRACT_SHA, image=CONTRACT["image"], platform=CONTRACT["platform"],
                      sdk_inspect="dependencies_resolved_only_runtime_not_tested",
                      source_sha256={name: sha(read_source(ROOT, name)) for name in
                                     ("prepare.py", "container.py", "backend.py", "contract.py")},
                      runtime={name: sha(raw) for name, raw in runtime.items()},
                      private={"cas.json": sha(fixture_raw), "cases-index.json": sha(cases_raw), "requirements.lock": sha(lock),
                               "dependency-lock.json": sha(dependency_raw)},
                      inputs=manifest["inputs"], outputs=manifest["outputs"])
        save(destination / "controle/manifest.json", encode(record))
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--case", required=True, choices=("complet", "manquant", "contradiction", "hostile"))
    args = parser.parse_args()
    try:
        print(prepare(args.destination, args.case))
    except (OSError, ValueError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
