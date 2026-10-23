#!/usr/bin/env python3
"""Prepare une definition Claude Code/Agent SDK. Aucun modele ni agent lance."""

import argparse
import json
from pathlib import Path
import sys

from preparer_agent import REFERENCES, _preparer, charger_json, configurer_sorties, empreinte_requete, texte


def preparer(mandat, capacites=None):
    catalogue = charger_json(REFERENCES / "profils-modeles-claude.json")
    requete = _preparer(mandat, capacites, catalogue)
    commun = requete["parametres_demandes"]
    nom = commun["task_name"].replace("_", "-")
    parametres = {"agents": {nom: {
        "description": texte(mandat["objectif"], "objectif"),
        "prompt": commun["message"], "model": commun["model"], "effort": commun["reasoning_effort"],
    }}}
    # The shared prompt validator's Codex wire keys never leave this exporter.
    requete.update(version=1, format="orka-claude-agent-definitions", hote="claude",
                   empreinte_requete=empreinte_requete(parametres), parametres_demandes=parametres,
                   verification_outils="mandat_documentaire_permissions_a_configurer_dans_hote")
    return requete


def main():
    configurer_sorties()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mandat", required=True, type=Path)
    parser.add_argument("--capacites", type=Path)
    parser.add_argument("--output", type=Path, help="Nouveau fichier uniquement")
    args = parser.parse_args()
    try:
        requete = preparer(charger_json(args.mandat), charger_json(args.capacites) if args.capacites else None)
        raw = json.dumps(requete, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.resolve() == Path(requete["sortie_attendue"]).resolve():
                raise ValueError("La requete ne doit pas remplacer le livrable attendu")
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(raw)
        else:
            sys.stdout.write(raw)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Erreur : {error}\n")


if __name__ == "__main__":
    main()
