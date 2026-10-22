#!/usr/bin/env python3
"""Verification du depot et du paquet, sans lancer de modele ni modifier de mission."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote
from zipfile import ZipFile

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/orka"


def verifier_format():
    contenu = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", contenu, re.S)
    if not frontmatter:
        raise ValueError("Frontmatter YAML absent")
    donnees = yaml.safe_load(frontmatter[1])
    if not isinstance(donnees, dict) or donnees.get("name") != "orka":
        raise ValueError("Nom du skill invalide")
    if not isinstance(donnees.get("description"), str) or not donnees["description"].strip():
        raise ValueError("Description du skill absente")
    if donnees.get("license") != "MIT":
        raise ValueError("Licence du skill incoherente")
    metadata = donnees.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Version du skill invalide")
    ref = os.environ.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/") and ref != "refs/tags/v" + version:
        raise ValueError("Le tag ne correspond pas a la version du skill")
    print("Format du skill valide, version " + version, flush=True)
    return version


def ancres(contenu):
    resultat = set(re.findall(r'(?:id|name)="([^"]+)"', contenu))
    deja = {}
    for titre in re.findall(r"^#{1,6}\s+(.+)$", contenu, re.M):
        base = re.sub(r"[^\w\- ]", "", titre.lower()).replace(" ", "-")
        numero = deja.get(base, 0)
        deja[base] = numero + 1
        resultat.add(base if not numero else base + "-" + str(numero))
    return resultat


def verifier_liens():
    # Index publics uniquement : les captures brutes gardent leurs liens historiques.
    fichiers = [ROOT / "README.md", ROOT / "README.fr.md", ROOT / "AGENTS.md",
                ROOT / "evals/README.md", *sorted((ROOT / "evals").glob("*/README.md")),
                *sorted((ROOT / "docs").rglob("*.md")), *sorted(SKILL.rglob("*.md"))]
    total, erreurs = 0, []
    for fichier in fichiers:
        for lien in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', fichier.read_text(encoding="utf-8")):
            lien = lien.strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", lien):
                continue
            chemin, _, ancre = lien.partition("#")
            cible = (fichier.parent / unquote(chemin)).resolve() if chemin else fichier
            total += 1
            if not cible.is_file():
                erreurs.append(str(fichier.relative_to(ROOT)) + " -> " + lien)
            elif ancre and cible.suffix == ".md" and unquote(ancre) not in ancres(cible.read_text(encoding="utf-8")):
                erreurs.append(str(fichier.relative_to(ROOT)) + " -> ancre " + lien)
    if erreurs:
        raise ValueError("Liens locaux invalides :\n" + "\n".join(erreurs))
    print(f"{total} liens locaux valides", flush=True)


def verifier_paquet(version):
    with tempfile.TemporaryDirectory(prefix="orka-verification-") as dossier:
        archive = Path(dossier) / "orka.zip"
        subprocess.run([sys.executable, "-B", str(ROOT / "install.py"), "--archive", str(archive)], check=True)
        with ZipFile(archive) as paquet:
            if paquet.testzip() is not None:
                raise ValueError("Archive corrompue")
            attendus = {"orka/" + f.relative_to(SKILL).as_posix(): f for f in SKILL.rglob("*")
                        if f.is_file() and not any(p in ("__pycache__", ".DS_Store") for p in f.relative_to(SKILL).parts)
                        and f.suffix != ".pyc"}
            attendus["orka/LICENSE"] = ROOT / "LICENSE"
            if set(paquet.namelist()) != set(attendus) or len(paquet.namelist()) != len(attendus):
                raise ValueError("Contenu du paquet incoherent")
            for nom, fichier in attendus.items():
                if paquet.read(nom) != fichier.read_bytes():
                    raise ValueError("Fichier different dans le paquet : " + nom)
            if ('version: "' + version + '"') not in paquet.read("orka/SKILL.md").decode("utf-8"):
                raise ValueError("Version du paquet incoherente")
    print("Paquet portable et version verifies", flush=True)


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    version = verifier_format()
    verifier_liens()
    # Les tests d'installation executent toutes les suites du skill deplace.
    subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    verifier_paquet(version)


if __name__ == "__main__":
    main()
