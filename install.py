#!/usr/bin/env python3
"""Install the bundled Orka skill or build its portable ZIP. No network calls."""

import argparse
import os
from pathlib import Path
import shutil
import sys
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / ".agents" / "skills" / "orka"
IGNORED = {"__pycache__", ".DS_Store"}


def skill_files():
    for path in sorted(SOURCE.rglob("*")):
        relative = path.relative_to(SOURCE)
        if path.is_file() and not any(part in IGNORED for part in relative.parts) and path.suffix != ".pyc":
            yield path, relative


def destination_for(agent, project=None):
    root = Path(project).expanduser().resolve() if project else Path.home()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    return root / (".agents" if agent == "codex" else ".claude") / "skills" / "orka"


def install(destination):
    destination = Path(destination).expanduser().absolute()
    if os.path.lexists(destination):
        raise FileExistsError(f"Destination already exists; nothing changed: {destination}")
    # Let copytree create the destination exclusively; never merge into an installation.
    shutil.copytree(SOURCE, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    shutil.copy2(ROOT / "LICENSE", destination / "LICENSE")
    return destination


def package(destination):
    destination = Path(destination).expanduser().absolute()
    if destination.suffix.lower() != ".zip":
        raise ValueError("Archive path must end in .zip")
    if os.path.lexists(destination):
        raise FileExistsError(f"Archive already exists; nothing changed: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "x", compression=ZIP_DEFLATED) as archive:
        for path, relative in skill_files():
            archive.write(path, (Path("orka") / relative).as_posix())
        archive.write(ROOT / "LICENSE", "orka/LICENSE")
    return destination


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agent", choices=("codex", "claude"), help="Install for this assistant (user scope by default)")
    mode.add_argument("--destination", type=Path, help="Exact skill directory for another Agent Skills host")
    mode.add_argument("--archive", type=Path, help="Build a ZIP containing orka/SKILL.md and all resources")
    parser.add_argument("--project", type=Path, help="Install for this existing project instead of the current user; requires --agent")
    args = parser.parse_args()
    if args.project is not None and args.agent is None:
        parser.error("--project requires --agent")
    try:
        if args.archive is not None:
            print(f"Archive: {package(args.archive)}")
        else:
            destination = destination_for(args.agent, args.project) if args.agent else args.destination
            installed = install(destination)
            print(f"Installed: {installed}")
            print(f"Getting-started guide (English): {installed / 'GUIDE.md'}")
            print(f"Guide de démarrage (français): {installed / 'GUIDE.fr.md'}")
            invocation = "$orka" if args.agent == "codex" else "/orka" if args.agent == "claude" else "Orka,"
            print(f"Next message: {invocation} Show me the getting-started guide and help me choose my first mission.")
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
