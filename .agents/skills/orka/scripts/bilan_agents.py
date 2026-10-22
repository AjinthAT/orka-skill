#!/usr/bin/env python3
"""Bilan de tentatives et mesures fournies. Aucun collecteur ni appel de modele."""

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path
import re
import sys

from preparer_agent import charger_json, configurer_sorties, texte


def objet(value, champs, obligatoires):
    if not isinstance(value, dict) or set(value) - champs or obligatoires - set(value):
        raise ValueError("Objet incomplet ou champs inconnus : " + ", ".join(sorted(champs)))
    return value


def entier(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Entier attendu, minimum {minimum}")
    return value


def bilan(document):
    objet(document, {"version", "mission", "couverture", "tentatives"},
          {"version", "mission", "couverture", "tentatives"})
    if type(document["version"]) is not int or document["version"] != 1:
        raise ValueError("Version attendue : 1")
    mission = texte(document["mission"], "mission")
    if document["couverture"] not in ("partielle", "complete_declaree"):
        raise ValueError("Couverture attendue : partielle ou complete_declaree")
    if not isinstance(document["tentatives"], list):
        raise ValueError("tentatives doit etre une liste")

    taches, mesures, lignes, couts = defaultdict(dict), set(), [], defaultdict(list)
    champs = {"tache", "tentative", "agent_id", "role", "modele_applique", "effort_applique",
              "etat", "preuve", "mesure", "cout"}
    for item in document["tentatives"]:
        objet(item, champs, champs - {"modele_applique", "effort_applique", "mesure", "cout"})
        tache = texte(item["tache"], "tache")
        numero = entier(item["tentative"], 1)
        if numero in taches[tache]:
            raise ValueError("Tentative dupliquee")
        for key in ("agent_id", "role", "preuve"):
            texte(item[key], key)
        for key in ("modele_applique", "effort_applique"):
            if item.get(key) is not None:
                texte(item[key], key)
        etat = item["etat"]
        if etat not in ("accepte", "a_corriger", "non_revu", "interrompu"):
            raise ValueError("Etat de resultat inconnu")
        mesure, cout = item.get("mesure"), item.get("cout")
        if mesure is not None:
            cles = {"id", "source", "perimetre", "entree", "sortie"}
            objet(mesure, cles, cles)
            identifiant = texte(mesure["id"], "mesure.id")
            texte(mesure["source"], "mesure.source")
            if identifiant in mesures:
                raise ValueError("Mesure dupliquee")
            if mesure["perimetre"] != "tentative_exclusive":
                raise ValueError("Seul un total exclusif de tentative est additionnable")
            entier(mesure["entree"])
            entier(mesure["sortie"])
            mesures.add(identifiant)
        if cout is not None:
            cles = {"nature", "montant", "devise", "source"}
            objet(cout, cles, cles)
            texte(cout["source"], "cout.source")
            if cout["nature"] not in ("constate", "estime"):
                raise ValueError("Nature de cout inconnue")
            if not isinstance(cout["devise"], str) or not re.fullmatch(r"[A-Z]{3}", cout["devise"]):
                raise ValueError("Devise attendue sur trois lettres majuscules")
            # Montants decimaux bornes : pas de float, NaN, exposant ou arrondi silencieux.
            if not isinstance(cout["montant"], str) or not re.fullmatch(r"\d{1,18}(?:\.\d{1,9})?", cout["montant"]):
                raise ValueError("Montant decimal positif ou nul attendu en texte")
            couts[(cout["nature"], cout["devise"])].append(Decimal(cout["montant"]))
        taches[tache][numero] = etat
        lignes.append(dict(item, tache=tache, mesure=mesure, cout=cout,
                           modele_applique=item.get("modele_applique"),
                           effort_applique=item.get("effort_applique")))

    for numeros in taches.values():
        if sorted(numeros) != list(range(1, len(numeros) + 1)):
            raise ValueError("Fournir toutes les tentatives depuis 1 pour chaque tache incluse")
    revues = [essais[1] for essais in taches.values() if essais[1] in ("accepte", "a_corriger")]
    connues = [ligne["mesure"] for ligne in lignes if ligne["mesure"] is not None]
    entree = sum(m["entree"] for m in connues) if connues else None
    sortie = sum(m["sortie"] for m in connues) if connues else None
    with localcontext() as contexte:
        contexte.prec = 40 + len(str(len(lignes)))
        montants = [{"nature": nature, "devise": devise, "montant": format(sum(valeurs), "f"),
                     "tentatives_renseignees": len(valeurs)}
                    for (nature, devise), valeurs in sorted(couts.items())]
    return {
        "version": 1, "mission": mission, "couverture_declaree": document["couverture"],
        "taches": len(taches), "tentatives": len(lignes),
        "reprises": len(lignes) - len(taches),
        "acceptation_initiale": {"acceptees": revues.count("accepte"), "revues": len(revues)},
        "etats_tentatives": dict(Counter(ligne["etat"] for ligne in lignes)),
        "etats_taches": dict(Counter(essais[max(essais)] for essais in taches.values())),
        "tokens": {"tentatives_mesurees": len(connues), "tentatives_sans_mesure": len(lignes) - len(connues),
                   "entree_connue": entree, "sortie_connue": sortie,
                   "total_connu": entree + sortie if connues else None},
        "couts": montants, "tentatives_sans_cout": sum(ligne["cout"] is None for ligne in lignes),
        "details": lignes,
        "limites": "Donnees fournies, non verifiees aupres du moteur ; totaux connus seulement. "
                   "Aucune collecte, conversion de devise, facturation ou limite de budget appliquee.",
    }


def main():
    configurer_sorties()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fichier", type=Path, help="Releve JSON normalise, version 1")
    args = parser.parse_args()
    try:
        resultat = bilan(charger_json(args.fichier))
    except (OSError, ValueError, InvalidOperation) as exc:
        parser.exit(2, f"Erreur : {exc}\n")
    json.dump(resultat, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
