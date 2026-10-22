#!/usr/bin/env python3
"""Diagnostic local Orka en lecture seule. Bibliotheque standard, aucun modele lance."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import sys
from urllib.parse import unquote, urlsplit


IGNORES = {"__pycache__", ".DS_Store"}
ESSENTIELS = ("SKILL.md", "GUIDE.md", "GUIDE.fr.md", "LICENSE")
MAX_TEXTE = 1024 * 1024


def lien_special(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def ouvrir_local(racine, chemin):
    """Verifier chaque composant avant ouverture, puis l'identite du fichier ouvert."""
    relatif = chemin.relative_to(racine)
    courant = racine
    for morceau in relatif.parts:
        courant = courant / morceau
        info = courant.lstat()
        if lien_special(info):
            raise ValueError("Lien symbolique ou point de reanalyse non suivi")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("La cible n'est pas un fichier ordinaire")
    fd = os.open(chemin, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        ouvert = os.fstat(fd)
        if not stat.S_ISREG(ouvert.st_mode) or (info.st_dev, info.st_ino) != (ouvert.st_dev, ouvert.st_ino):
            raise ValueError("Le fichier a change pendant son ouverture")
        flux = os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise
    return flux


def lire_texte(racine, chemin):
    with ouvrir_local(racine, chemin) as flux:
        contenu = flux.read(MAX_TEXTE + 1)
    if len(contenu) > MAX_TEXTE:
        raise ValueError("Document texte depassant la limite de 1 Mio")
    return contenu.decode("utf-8")


def scalaire(texte):
    if texte.startswith('"'):
        valeur = json.loads(texte)
        if not isinstance(valeur, str):
            raise ValueError("Une chaine est attendue")
        return valeur
    if texte.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", texte):
            raise ValueError("Chaine simple mal fermee")
        return texte[1:-1].replace("''", "'")
    if not texte or texte[0] in "[{&*!|>@%?-" or " #" in texte or ": " in texte:
        raise ValueError("Scalaire YAML non pris en charge ; utiliser une chaine sur une ligne")
    if texte.lower() in {"null", "true", "false", "~", ".nan", ".inf"} or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", texte):
        raise ValueError("Une chaine est attendue")
    return texte


def metadonnees(contenu):
    """Sous-ensemble explicite : scalaires sur une ligne et mapping metadata a deux espaces."""
    lignes = contenu.splitlines()
    if not lignes or lignes[0] != "---":
        raise ValueError("Frontmatter absent")
    try:
        fin = lignes.index("---", 1)
    except ValueError:
        raise ValueError("Frontmatter non ferme") from None
    valeurs, metadata = {}, {}
    dans_metadata = False
    for ligne in lignes[1:fin]:
        if not ligne.strip() or ligne.lstrip().startswith("#"):
            continue
        nested = re.fullmatch(r"  ([a-zA-Z][\w-]*): +(.+)", ligne)
        top = re.fullmatch(r"([a-zA-Z][\w-]*):(?: +(.+))?", ligne)
        if nested and dans_metadata:
            cle, texte = nested.groups()
            if cle in metadata:
                raise ValueError("Cle metadata dupliquee : " + cle)
            metadata[cle] = scalaire(texte.strip())
        elif top:
            cle, texte = top.groups()
            if cle in valeurs:
                raise ValueError("Cle dupliquee : " + cle)
            dans_metadata = cle == "metadata"
            if dans_metadata:
                if texte is not None:
                    raise ValueError("metadata doit etre un mapping indente de deux espaces")
                valeurs[cle] = metadata
            else:
                valeurs[cle] = scalaire((texte or "").strip())
        else:
            raise ValueError("Format YAML non pris en charge")
    if valeurs.get("name") != "orka" or not valeurs.get("description", "").strip() or valeurs.get("license") != "MIT":
        raise ValueError("name: orka, description non vide et license: MIT sont requis")
    version = metadata.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("metadata.version doit etre une version x.y.z")
    return version


def sans_blocs_code(texte):
    sortie, cloture = [], None
    for ligne in texte.splitlines():
        marque = re.match(r"^ {0,3}(`{3,}|~{3,})", ligne)
        if marque:
            fence = marque.group(1)
            if cloture is None:
                cloture = fence
            elif fence[0] == cloture[0] and len(fence) >= len(cloture):
                cloture = None
        elif cloture is None:
            sortie.append(ligne)
    return "\n".join(sortie)


def ancres(texte):
    texte = sans_blocs_code(texte)
    resultat = set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', texte))
    deja = {}
    for titre in re.findall(r"^#{1,6}\s+(.+)$", texte, re.M):
        base = re.sub(r"[^\w\- ]", "", titre.lower()).replace(" ", "-")
        numero = deja.get(base, 0)
        deja[base] = numero + 1
        resultat.add(base if not numero else base + "-" + str(numero))
    return resultat


def liens(texte):
    texte = sans_blocs_code(texte)
    inline = re.findall(r'!?\[[^\]]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+["\'][^\n]*["\'])?\s*\)', texte)
    references = re.findall(r'^ {0,3}\[[^\]]+\]:\s*(<[^>\n]+>|\S+)', texte, re.M)
    html = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', texte)
    return set(cible.strip("<>") for cible in inline + references + html)


def inspecter(dossier, constats, prefixe):
    def ajouter(identifiant, etat, preuve, action):
        constats.append(dict(id=prefixe + identifiant, etat=etat, preuve=preuve, action=action))

    resultat = dict(dossier=str(dossier), version_declaree=None, empreintes={}, inventaire_complet=False)
    try:
        racine = Path(dossier).expanduser().resolve(strict=True)
        if not racine.is_dir():
            raise ValueError("Un dossier de skill est attendu")
        resultat["dossier"] = str(racine)
        resultat["version_declaree"] = metadonnees(lire_texte(racine, racine / "SKILL.md"))
    except (OSError, ValueError, UnicodeError, RuntimeError) as erreur:
        ajouter("metadonnees", "anomalie", str(erreur), "Verifier le dossier indique et le format documente de SKILL.md.")
        return resultat
    ajouter("metadonnees", "conforme", "Version declaree : " + resultat["version_declaree"], "Aucune action.")
    fichiers, textes = {}, {}
    lecture_echouee = False

    def parcourir(dossier_courant):
        nonlocal lecture_echouee
        try:
            with os.scandir(dossier_courant) as entrees:
                for entree in sorted(entrees, key=lambda e: e.name):
                    if entree.name in IGNORES or entree.name.endswith(".pyc"):
                        continue
                    chemin = Path(entree.path)
                    nom = chemin.relative_to(racine).as_posix()
                    try:
                        info = entree.stat(follow_symlinks=False)
                        if lien_special(info):
                            raise ValueError("Lien symbolique ou point de reanalyse non suivi")
                        if stat.S_ISDIR(info.st_mode):
                            parcourir(chemin)
                        elif stat.S_ISREG(info.st_mode):
                            fichiers[nom] = chemin
                            empreinte = hashlib.sha256()
                            with ouvrir_local(racine, chemin) as flux:
                                for bloc in iter(lambda: flux.read(1024 * 1024), b""):
                                    empreinte.update(bloc)
                            resultat["empreintes"][nom] = empreinte.hexdigest()
                            if chemin.suffix.lower() == ".md":
                                textes[nom] = lire_texte(racine, chemin)
                        else:
                            raise ValueError("Fichier special non lu")
                    except (OSError, ValueError, UnicodeError) as erreur:
                        lecture_echouee = True
                        ajouter("lecture", "anomalie", nom + " : " + str(erreur), "Verifier la cible et ses droits sans la remplacer.")
        except OSError as erreur:
            lecture_echouee = True
            ajouter("lecture", "anomalie", str(erreur), "Verifier les droits du dossier.")

    parcourir(racine)
    resultat["inventaire_complet"] = not lecture_echouee
    for nom in ESSENTIELS:
        if nom not in resultat["empreintes"]:
            ajouter("ressource_absente", "anomalie", nom, "Comparer avec une archive connue ; conserver les adaptations avant remplacement.")
    externes, locaux = 0, 0
    for nom, texte in sorted(textes.items()):
        for cible in sorted(liens(texte)):
            try:
                if PureWindowsPath(cible).drive:
                    raise ValueError("Chemin absolu ou reseau non suivi")
                url = urlsplit(cible)
                if url.scheme == "file":
                    raise ValueError("URL fichier non suivie")
                if url.scheme or url.netloc:
                    externes += 1
                    continue
                chemin = unquote(url.path)
                if Path(chemin).is_absolute() or PureWindowsPath(chemin).drive or "\\" in chemin:
                    raise ValueError("Chemin absolu ou non portable non suivi")
                destination = Path(os.path.normpath(str(fichiers[nom].parent / chemin))) if chemin else fichiers[nom]
                relatif = destination.relative_to(racine).as_posix()
                if relatif not in resultat["empreintes"]:
                    raise ValueError("Cible absente, illisible ou non suivie : " + relatif)
                if url.fragment and destination.suffix.lower() == ".md":
                    if relatif not in textes or unquote(url.fragment) not in ancres(textes[relatif]):
                        raise ValueError("Ancre Markdown absente : " + relatif + "#" + unquote(url.fragment))
                locaux += 1
            except (OSError, ValueError) as erreur:
                ajouter("lien_local", "anomalie", nom + " : " + str(erreur), "Verifier le lien et la ressource dans le dossier autorise.")
    ajouter("liens_locaux", "conforme", f"{locaux} liens locaux resolus ; exemples en blocs de code exclus.", "Consulter les anomalies eventuelles ci-dessus.")
    ajouter("liens_externes", "non_verifie", f"{externes} liens externes non ouverts.", "Verifier leur disponibilite separement si necessaire.")
    return resultat


def diagnostiquer(dossier, reference=None):
    constats = []
    installation = inspecter(dossier, constats, "installation.")
    integrite, comparaison = "non_verifiee", None
    if reference is not None:
        debut = len(constats)
        comparaison = inspecter(reference, constats, "reference.")
        reference_valide = not any(c["etat"] == "anomalie" for c in constats[debut:])
        installation_comparable = installation["version_declaree"] is not None and installation["inventaire_complet"]
        if reference_valide and installation_comparable:
            attendus, reels = comparaison["empreintes"], installation["empreintes"]
            differences = dict(manquants=sorted(attendus.keys() - reels.keys()), supplementaires=sorted(reels.keys() - attendus.keys()),
                               modifies=sorted(n for n in attendus.keys() & reels.keys() if attendus[n] != reels[n]))
            differente = any(differences.values())
            integrite = "differente" if differente else "conforme"
            constats.append(dict(id="comparaison", etat="anomalie" if differente else "conforme", preuve=differences,
                                 action="Conserver les adaptations ; examiner les differences avant tout remplacement." if differente else "Aucune action."))
    constats.append(dict(id="activation_hote", etat="non_verifie", preuve="Aucun assistant ni modele n'a ete lance.", action="Verifier la reconnaissance du skill dans une session de l'hote."))
    constats.append(dict(id="capacites_hote", etat="non_verifie", preuve="Modeles, outils et delegation non interroges.", action="Verifier les capacites natives de la session si elles sont necessaires."))
    constats.append(dict(id="integrite_reference", etat="non_verifie" if integrite == "non_verifiee" else "anomalie" if integrite == "differente" else "conforme",
                         preuve=integrite, action="Fournir une reference connue pour une comparaison complete ; son authenticite reste a etablir."))
    resume = {etat: sum(c["etat"] == etat for c in constats) for etat in ("conforme", "anomalie", "non_verifie")}
    return dict(version=1, installation=installation, reference=comparaison, integrite_reference=integrite,
                activation_hote="non_verifiee", capacites_hote="non_verifiees", constats=constats, resume=resume,
                code=1 if resume["anomalie"] else 0)


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", required=True, type=Path, help="Dossier de skill explicite, jamais modifie")
    parser.add_argument("--reference", type=Path, help="Dossier d'une reference connue, jamais modifie")
    parser.add_argument("--json", action="store_true", help="Rapport JSON version 1 sur la sortie standard")
    args = parser.parse_args()
    rapport = diagnostiquer(args.skill_dir, args.reference)
    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
    else:
        print("Orka — diagnostic en lecture seule")
        print("Dossier : " + rapport["installation"]["dossier"])
        print("Version declaree : " + str(rapport["installation"]["version_declaree"]))
        print("Integrite face a la reference : " + rapport["integrite_reference"])
        for constat in rapport["constats"]:
            preuve = json.dumps(constat["preuve"], ensure_ascii=False) if isinstance(constat["preuve"], dict) else constat["preuve"]
            print(f"[{constat['etat']}] {constat['id']} : {preuve}\n  {constat['action']}")
        print("Activation et capacites de l'hote : non verifiees.")
    return rapport["code"]


if __name__ == "__main__":
    sys.exit(main())
