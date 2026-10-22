#!/usr/bin/env python3
"""Recontrole local des artefacts captures. Ne lance aucun agent ni modele."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def verifier(cellule):
    artefacts = ROOT / "executions" / cellule["id"] / "artefacts"
    resultat = {"cellule": cellule["id"], "constats": {}, "commandes": []}
    changements = []
    for nom, empreinte in cellule["entrees_sha256"].items():
        fichier = artefacts / nom
        if not fichier.is_file() or hashlib.sha256(fichier.read_bytes()).hexdigest() != empreinte:
            changements.append(nom)
    resultat["entrees_modifiees"] = changements
    reponse = (artefacts / "output/response.txt").read_text(encoding="utf-8")
    resultat["reponse_octets"] = len(reponse.encode("utf-8"))
    if cellule["cas"] == "01-annonce":
        try:
            annonce = json.loads(reponse)
            valide = isinstance(annonce, dict) and set(annonce) == {"titre", "texte"} and all(isinstance(v, str) for v in annonce.values())
        except ValueError:
            annonce, valide = {}, False
        resultat["constats"]["json_exact"] = valide
        if valide:
            resultat["constats"].update(titre_mots=len(annonce["titre"].split()), texte_mots=len(annonce["texte"].split()))
    else:
        livrable = (artefacts / "livrable.md").read_text(encoding="utf-8")
        resultat["constats"]["livrable_mots"] = len(livrable.split())
    if cellule["cas"] == "02-etude":
        with (artefacts / "observations.csv").open(encoding="utf-8", newline="") as fichier:
            lignes = list(csv.DictReader(fichier))
        connues = [int(l["attente_premier_accueil_minutes"]) for l in lignes if l["attente_premier_accueil_minutes"]]
        resultat["constats"]["donnees_reference"] = {"connues": len(connues), "inconnues": len(lignes)-len(connues), "superieures_a_5": sum(v > 5 for v in connues)}
    if cellule["cas"] == "03-reprise":
        with tempfile.TemporaryDirectory(prefix="orka-controle-prototype-") as dossier:
            copie = Path(dossier) / "prototype"
            shutil.copytree(artefacts, copie, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            commandes = [
                ["-m", "unittest", "-v", "test_app"],
                ["-c", 'import app,json; print(json.dumps({str(v):app.priorite(v) for v in (0,5,7,8,None)}))'],
            ]
            for arguments in commandes:
                try:
                    proc = subprocess.run([sys.executable, "-B", *arguments], cwd=copie, capture_output=True, text=True, encoding="utf-8", timeout=30)
                    resultat["commandes"].append({"arguments": arguments, "code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
                except subprocess.TimeoutExpired:
                    resultat["commandes"].append({"arguments": arguments, "code": None, "erreur": "delai_30_secondes"})
            fonction = resultat["commandes"][1]
            try:
                resultat["constats"]["fonction_conforme"] = fonction["code"] == 0 and json.loads(fonction["stdout"]) == {"0":"normale", "5":"normale", "7":"normale", "8":"prioritaire", "None":"inconnue"}
            except (KeyError, ValueError):
                resultat["constats"]["fonction_conforme"] = False
    return resultat


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    destination = ROOT / "verifications"
    destination.mkdir(exist_ok=True)
    for cellule in manifest["cellules"]:
        if cellule["statut"] == "termine":
            resultat = verifier(cellule)
            (destination / (cellule["id"] + ".json")).write_text(json.dumps(resultat, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            print(cellule["id"], json.dumps(resultat["constats"], ensure_ascii=False))


if __name__ == "__main__":
    main()
