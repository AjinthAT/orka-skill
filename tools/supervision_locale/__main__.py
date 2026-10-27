"""CLI explicitement hors ligne ; aucune entrée ne permet un appel modèle."""

import argparse
import json
import sqlite3
import sys

from .controleur import Controleur, INCIDENTS, creer, etat, suspendre


def main():
    parser = argparse.ArgumentParser(description="AUT-02A : recette locale de processus fixes, aucun modèle")
    commandes = parser.add_subparsers(dest="commande", required=True)
    demo = commandes.add_parser("demo", help="Créer puis exécuter un essai neuf")
    demo.add_argument("--scenario", choices=["reprise-simple"], required=True)
    demo.add_argument("--destination", required=True)
    demo.add_argument("--incident", choices=INCIDENTS, default="aucun")
    demo.add_argument("--sans-reprise", action="store_true")
    demo.add_argument("--maximum-t1", type=int, choices=[1, 2], default=2)
    demo.add_argument("--delai", type=float, default=2)
    reprise = commandes.add_parser("resume", help="Réconcilier la même base et poursuivre si autorisé")
    reprise.add_argument("--destination", required=True)
    reprise.add_argument("--reprendre-suspension", action="store_true")
    for nom in ("etat", "suspendre"):
        cmd = commandes.add_parser(nom)
        cmd.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        if args.commande == "demo":
            creer(args.destination, args.incident, not args.sans_reprise, args.maximum_t1, args.delai)
        if args.commande in ("demo", "resume"):
            resultat = Controleur(args.destination).run(getattr(args, "reprendre_suspension", False))
            code = 0 if resultat["etat"] == "succes" else 2
        elif args.commande == "suspendre":
            suspendre(args.destination)
            resultat, code = {"etat": "suspendue", "appels_modeles": 0}, 0
        else:
            resultat, code = etat(args.destination), 0
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as erreur:
        resultat, code = {"etat": "refuse", "motif": str(erreur), "appels_modeles": 0}, 2
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
