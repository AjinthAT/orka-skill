#!/usr/bin/env python3
"""Prepare un mandat et ses parametres. Aucun appel de modele ni lancement d'agent."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"


def charger_json(path):
    def sans_doublons(paires):
        resultat = {}
        for cle, valeur in paires:
            if cle in resultat:
                raise ValueError(f"Cle JSON dupliquee : {cle}")
            resultat[cle] = valeur
        return resultat

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=sans_doublons)


def texte(value, champ):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{champ} doit etre un texte non vide")
    return value.strip()


def liste(value, champ, obligatoire=False):
    if not isinstance(value, list) or (obligatoire and not value):
        raise ValueError(f"{champ} doit etre une liste" + (" non vide" if obligatoire else ""))
    return [texte(item, champ) for item in value]


def nom_lancement(mission_id, tache_id, role, tentative):
    nom = re.sub(r"[^a-z0-9_]+", "_", f"{mission_id}_{tache_id}_{role}".lower()).strip("_")
    identite = json.dumps([mission_id, tache_id, role, tentative], ensure_ascii=False)
    return nom[:48] + f"_a{tentative}_" + hashlib.sha256(identite.encode()).hexdigest()[:10]


def empreinte_requete(parametres):
    contenu = json.dumps(parametres, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(contenu.encode()).hexdigest()


def preparer(mandat, capacites=None):
    if not isinstance(mandat, dict):
        raise ValueError("Le mandat doit etre un objet JSON")
    champs = {"mission_id", "tache_id", "role", "objectif", "contexte", "entrees", "sortie",
              "criteres", "acceptation", "outils_autorises", "limites", "mode", "profil", "modele", "effort", "tentative"}
    inconnus = set(mandat) - champs
    if inconnus:
        raise ValueError("Champs inconnus : " + ", ".join(sorted(inconnus)))
    catalogue = charger_json(REFERENCES / "profils-modeles.json")
    role = texte(mandat.get("role"), "role")
    if role not in catalogue["roles"]:
        raise ValueError(f"Role inconnu : {role}")
    profil = mandat.get("profil", catalogue["roles"][role])
    if not isinstance(profil, str) or profil not in catalogue["profils"]:
        raise ValueError("Profil inconnu")
    reglage = catalogue["profils"][profil]
    modele = texte(mandat.get("modele", reglage["modele"]), "modele")
    effort = texte(mandat.get("effort", reglage["effort"]), "effort")
    if modele not in catalogue["modeles"] or effort not in catalogue["modeles"][modele]:
        raise ValueError("Modele ou effort absent du catalogue ; verifier avant de le modifier")
    if capacites is not None:
        if (not isinstance(capacites, dict)
                or not all(isinstance(k, str) and isinstance(v, list)
                           and all(isinstance(x, str) for x in v)
                           for k, v in capacites.items())):
            raise ValueError("Les capacites doivent associer chaque modele a ses efforts disponibles")
        if effort not in capacites.get(modele, []):
            raise ValueError("Modele ou effort indisponible dans les capacites fournies ; aucun remplacement automatique")
    contenu = {key: texte(mandat.get(key), key) for key in
               ("mission_id", "tache_id", "objectif", "sortie", "acceptation")}
    for key in ("contexte", "entrees", "outils_autorises", "limites", "criteres"):
        contenu[key] = liste(mandat.get(key, []), key, obligatoire=(key == "criteres"))
    mode = mandat.get("mode", "revue" if profil == "revue" else "production")
    if mode not in ("production", "analyse", "revue", "correction", "reprise"):
        raise ValueError("Mode inconnu")
    if mode in ("revue", "correction", "reprise") and not contenu["entrees"]:
        raise ValueError(f"Le mode {mode} exige une entree identifiant le resultat ou l'etat concerne")
    tentative = mandat.get("tentative", 1)
    if type(tentative) is not int or tentative < 1:
        raise ValueError("tentative doit etre un entier positif")
    equipe = next(key for key, roles in catalogue["equipes"].items() if role in roles)
    source_role = REFERENCES / "equipes" / (equipe + ".md")
    fiche = source_role.read_text()
    section = re.search(r"^## " + re.escape(role) + r"(?:\s[^\n]*)?\n.*?(?=^## |\Z)",
                        fiche, flags=re.M | re.S)
    if not section:
        raise ValueError("Fiche du role introuvable")
    commun = (REFERENCES / "prompts" / "consignes-communes.md").read_text().strip()
    nom = nom_lancement(contenu["mission_id"], contenu["tache_id"], role, tentative)
    prompt = (commun + "\n\n# Role attribue\n\nFiche source : " + str(source_role)
              + "\nLes liens relatifs de cette fiche sont relatifs a ce fichier.\n\n" + section.group().strip()
              + "\n\n# Mandat structure\n\nMode de travail : " + mode
              + "\nLes criteres ci-dessous sont indispensables sauf precision explicite du mandat."
              + "\n\n" + json.dumps(contenu, ensure_ascii=False, indent=2))
    parametres = {
        "task_name": nom,
        "fork_turns": "none",
        "model": modele,
        "reasoning_effort": effort,
        "message": prompt,
    }
    return {
        "version": 2,
        "version_catalogue": catalogue["version"],
        "empreinte_prompt": hashlib.sha256(prompt.encode()).hexdigest(),
        "empreinte_requete": empreinte_requete(parametres),
        "mission_id": contenu["mission_id"],
        "tache_id": contenu["tache_id"],
        "tentative": tentative,
        "role": role,
        "profil": profil,
        "mode": mode,
        "etat": "prepare_non_lance",
        "parametres_appliques": None,
        "verification_capacites": "declarees_par_appelant" if capacites is not None else "a_verifier_au_lancement",
        "sortie_attendue": contenu["sortie"],
        "parametres_demandes": parametres,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mandat", type=Path, required=True)
    parser.add_argument("--capacites", type=Path)
    parser.add_argument("--output", type=Path, help="Nouveau fichier de requete ; jamais ecrase")
    args = parser.parse_args()
    try:
        mandat = charger_json(args.mandat)
        capacites = charger_json(args.capacites) if args.capacites else None
        requete = preparer(mandat, capacites)
        sortie = json.dumps(requete, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.resolve() == Path(requete["sortie_attendue"]).resolve():
                raise ValueError("La requete ne doit pas remplacer le livrable attendu")
            with args.output.open("x") as fichier:
                fichier.write(sortie)
        else:
            sys.stdout.write(sortie)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Erreur : {exc}\n")


if __name__ == "__main__":
    main()
