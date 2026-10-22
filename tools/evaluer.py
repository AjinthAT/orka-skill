#!/usr/bin/env python3
"""Preparer et relire des evaluations fournies, sans lancer de modele ni de code inspecte."""

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import shutil
import stat
import sys


MAX_OCTETS = 16 * 1024 * 1024
ETATS = {"terminee", "interrompue", "hors_protocole"}
VERDICTS = {"satisfait", "non_satisfait", "non_verifie"}


def texte(v):
    if not isinstance(v, str) or not v.strip():
        raise ValueError("Texte non vide attendu")
    return v


def objet(v, champs, requis=None):
    if not isinstance(v, dict) or set(v) - set(champs) or set(champs if requis is None else requis) - set(v):
        raise ValueError("Objet incomplet ou champs inconnus : " + ", ".join(champs))
    return v


def liste(v, non_vide=False):
    if not isinstance(v, list) or (non_vide and not v):
        raise ValueError("Liste attendue" + (" non vide" if non_vide else ""))
    return v


def entier(v, minimum=0):
    if type(v) is not int or v < minimum:
        raise ValueError("Entier attendu, minimum " + str(minimum))
    return v


def nombre(v):
    if type(v) not in (int, float) or (type(v) is float and not math.isfinite(v)):
        raise ValueError("Nombre fini attendu")
    return v


def identifiant(v):
    texte(v)
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", v) or re.fullmatch(r"con|prn|aux|nul|com[1-9]|lpt[1-9]", v):
        raise ValueError("Identifiant non portable : " + v)
    return v


def relatif(v):
    texte(v)
    if ("\\" in v or PureWindowsPath(v).drive or PurePosixPath(v).is_absolute()
            or re.search(r'[<>:"|?*\x00-\x1f]', v)
            or any(p in ("", ".", "..") or p.endswith((".", " "))
                   or re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p) for p in v.split("/"))):
        raise ValueError("Chemin relatif portable attendu : " + v)
    return v


def lire(racine, nom):
    """Lecture d'un fichier ordinaire, sans suivre de lien sous la racine explicite."""
    chemin = racine
    for partie in relatif(nom).split("/"):
        chemin = chemin / partie
        info = chemin.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Lien ou point de reanalyse non suivi : " + nom)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Fichier ordinaire attendu : " + nom)
    fd = os.open(chemin, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        ouvert = os.fstat(fd)
        if (ouvert.st_dev, ouvert.st_ino) != (info.st_dev, info.st_ino):
            raise ValueError("Fichier modifie pendant l'ouverture : " + nom)
        flux = os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise
    with flux:
        brut = flux.read(MAX_OCTETS + 1)
    if len(brut) > MAX_OCTETS:
        raise ValueError("Fichier depassant 16 Mio : " + nom)
    return brut


def decoder(brut):
    def paires(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError("Cle JSON dupliquee : " + k)
            d[k] = v
        return d

    def constante(v):
        raise ValueError("Constante JSON non finie : " + v)

    return json.loads(brut.decode("utf-8"), object_pairs_hook=paires, parse_constant=constante)


def charger(fichier):
    fichier = Path(fichier).absolute()
    return decoder(lire(fichier.parent.resolve(strict=True), fichier.name))


def canon(v):
    return json.dumps(v, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(brut):
    return hashlib.sha256(brut).hexdigest()


def sceller(v):
    return dict(v, empreinte=sha(canon(v)))


def verifier_sceau(v):
    if not isinstance(v, dict) or "empreinte" not in v or v["empreinte"] != sha(canon({k: x for k, x in v.items() if k != "empreinte"})):
        raise ValueError("Empreinte du manifeste ou resultat incoherente")
    return v


def ecrire(fichier, v):
    # Creation exclusive : aucune sortie ni preuve precedente n'est remplacee.
    with Path(fichier).open("x", encoding="utf-8", newline="\n") as flux:
        flux.write(json.dumps(v, ensure_ascii=False, allow_nan=False, indent=2) + "\n")


def uniques(items):
    ids = [identifiant(x["id"]) for x in items]
    if len(set(ids)) != len(ids):
        raise ValueError("Identifiants dupliques")


def critere(c):
    objet(c, ("id", "description", "obligatoire", "type", "fichier", "chemin", "attendu", "minimum", "maximum"),
          ("id", "description", "obligatoire", "type"))
    identifiant(c["id"]); texte(c["description"])
    if type(c["obligatoire"]) is not bool or c["type"] not in ("json_egal", "json_nombre", "revue"):
        raise ValueError("Type de critere ou caractere obligatoire invalide")
    extras = set(c) - {"id", "description", "obligatoire", "type"}
    if c["type"] == "revue":
        if extras:
            raise ValueError("Une revue ne contient pas de controle automatique")
        return
    relatif(c.get("fichier"))
    for cle in liste(c.get("chemin")):
        if not isinstance(cle, str) and not (type(cle) is int and cle >= 0):
            raise ValueError("Chemin JSON : cles texte ou indices positifs attendus")
    if c["type"] == "json_egal":
        if extras != {"fichier", "chemin", "attendu"}:
            raise ValueError("json_egal exige fichier, chemin et attendu")
        canon(c["attendu"])
    else:
        if not extras <= {"fichier", "chemin", "minimum", "maximum"} or not extras & {"minimum", "maximum"}:
            raise ValueError("json_nombre exige au moins une borne")
        for cle in ("minimum", "maximum"):
            if cle in c:
                nombre(c[cle])
        if c.get("minimum", -math.inf) > c.get("maximum", math.inf):
            raise ValueError("Bornes inversees")


def valider_plan(p):
    objet(p, ("format", "id", "origine", "hypothese", "nature", "hote", "repetitions", "max_executions", "limites", "versions", "cas"))
    if type(p["format"]) is not int or p["format"] != 1 or p["nature"] not in ("simulation", "reelle"):
        raise ValueError("Format 1 et nature simulation/reelle attendus")
    identifiant(p["id"])
    for cle in ("origine", "hypothese", "hote"):
        texte(p[cle])
    entier(p["repetitions"], 1); entier(p["max_executions"], 1)
    for limite in liste(p["limites"], True):
        texte(limite)
    for v in liste(p["versions"], True):
        objet(v, ("id", "provenance", "instructions", "reglages_demandes"))
        identifiant(v["id"]); texte(v["provenance"])
        for f in liste(v["instructions"], True):
            relatif(f)
        if v["reglages_demandes"] is not None:
            objet(v["reglages_demandes"], ("modele", "effort"))
            for x in v["reglages_demandes"].values():
                texte(x)
    uniques(p["versions"])
    for c in liste(p["cas"], True):
        objet(c, ("id", "origine", "usage", "entrees", "prompt", "criteres"))
        identifiant(c["id"]); texte(c["origine"]); relatif(c["prompt"])
        if c["usage"] not in ("developpement", "reserve"):
            raise ValueError("Usage developpement/reserve attendu")
        for f in liste(c["entrees"]):
            relatif(f)
        for x in liste(c["criteres"], True):
            critere(x)
        uniques(c["criteres"])
        if not any(x["obligatoire"] for x in c["criteres"]):
            raise ValueError("Au moins un critere indispensable par cas")
    uniques(p["cas"])
    if len(p["cas"]) * len(p["versions"]) * p["repetitions"] > p["max_executions"]:
        raise ValueError("Nombre d'executions superieur a la limite du plan")


def figer(racine, noms):
    pieces, octets = {}, {}
    for i, nom in enumerate(sorted(set(noms)), 1):
        brut = lire(racine, nom)
        copie = f"pieces/f{i:04d}"
        pieces[nom] = dict(copie=copie, sha256=sha(brut))
        octets[copie] = brut
    return pieces, octets


def creer_dossier(cible, documents, nom_manifest, manifeste):
    cible.mkdir()  # Echec si la destination existe, meme vide ou symbolique.
    try:
        for nom, brut in documents.items():
            chemin = cible / nom
            chemin.parent.mkdir(parents=True, exist_ok=True)
            with chemin.open("xb") as f:
                f.write(brut)
        ecrire(cible / nom_manifest, sceller(manifeste))
    except BaseException:
        shutil.rmtree(cible)
        raise


def preparer(plan, racine=Path(".orka/evaluations")):
    fichier = Path(plan).absolute()
    p = charger(fichier)
    valider_plan(p)
    noms = [f for v in p["versions"] for f in v["instructions"]]
    noms += [f for c in p["cas"] for f in [c["prompt"], *c["entrees"]]]
    pieces, octets = figer(fichier.parent.resolve(strict=True), noms)
    # Les prompts sont du texte exact, jamais interpretes ni enrichis silencieusement.
    for c in p["cas"]:
        octets[pieces[c["prompt"]]["copie"]].decode("utf-8")
    executions = []
    for rep in range(1, p["repetitions"] + 1):
        for i, c in enumerate(p["cas"]):
            versions = p["versions"] if (rep + i) % 2 else list(reversed(p["versions"]))
            for v in versions:
                executions.append(dict(id=f"e{len(executions) + 1:04d}", cas=c["id"], version=v["id"], repetition=rep))
    manifeste = dict(format=1, plan=p, pieces=pieces, executions=executions)
    racine = Path(racine).expanduser().resolve()
    racine.mkdir(parents=True, exist_ok=True)
    cible = racine / p["id"]
    creer_dossier(cible, octets, "manifest.json", manifeste)
    return cible


def verifier_pieces(racine, pieces):
    for p in pieces.values():
        if sha(lire(racine, p["copie"])) != p["sha256"]:
            raise ValueError("Piece figee modifiee : " + p["copie"])


def ouvrir_campagne(dossier):
    racine = Path(dossier).expanduser().resolve(strict=True)
    m = verifier_sceau(decoder(lire(racine, "manifest.json")))
    objet(m, ("format", "plan", "pieces", "executions", "empreinte"))
    if type(m["format"]) is not int or m["format"] != 1:
        raise ValueError("Format de campagne attendu : 1")
    valider_plan(m["plan"])
    verifier_pieces(racine, m["pieces"])
    return racine, m


def empreinte_execution(m, execution):
    return sha(canon(dict(campagne=m["empreinte"], execution=execution)))


def valider_resultat(r, m, execution):
    objet(r, ("format", "execution", "empreinte_execution", "nature", "etat", "provenance", "sorties", "ecarts", "revues",
              "reglages_appliques", "tokens", "cout", "traces", "duree_observee"),
          ("format", "execution", "empreinte_execution", "nature", "etat", "provenance", "sorties", "ecarts", "revues"))
    if type(r["format"]) is not int or r["format"] != 1 or r["execution"] != execution["id"] or r["nature"] != m["plan"]["nature"]:
        raise ValueError("Resultat incompatible avec l'execution preparee")
    if r["empreinte_execution"] != empreinte_execution(m, execution):
        raise ValueError("Versions d'entrees du resultat incoherentes")
    if r["etat"] not in ETATS:
        raise ValueError("Un resultat ne peut pas confirmer une execution preparee seulement")
    objet(r["provenance"], ("source", "hote", "id_natif"))
    texte(r["provenance"]["source"]); texte(r["provenance"]["hote"])
    natif = r["provenance"]["id_natif"]
    if r["nature"] == "reelle":
        texte(natif)
    elif natif is not None:
        raise ValueError("Une simulation ne declare pas d'identifiant natif reel")
    sorties = liste(r["sorties"])
    for f in sorties:
        relatif(f)
    if len(set(sorties)) != len(sorties):
        raise ValueError("Sorties dupliquees")
    for x in liste(r["ecarts"]):
        texte(x)
    if r["etat"] == "hors_protocole" and not r["ecarts"]:
        raise ValueError("Un ecart de protocole exige son motif")
    criteres = next(c["criteres"] for c in m["plan"]["cas"] if c["id"] == execution["cas"])
    revues = {c["id"] for c in criteres if c["type"] == "revue"}
    if not isinstance(r["revues"], dict) or set(r["revues"]) - revues:
        raise ValueError("Revue inconnue ou surcharge d'un controle deterministe")
    for avis in r["revues"].values():
        objet(avis, ("etat", "auteur", "source", "preuve"))
        if avis["etat"] not in VERDICTS:
            raise ValueError("Etat de revue invalide")
        for k in ("auteur", "source", "preuve"):
            texte(avis[k])
    mesures = {k: r.get(k) for k in ("reglages_appliques", "tokens", "cout", "traces", "duree_observee")}
    if mesures["reglages_appliques"] is not None:
        objet(mesures["reglages_appliques"], ("modele", "effort", "source"))
        for v in mesures["reglages_appliques"].values():
            texte(v)
    if mesures["tokens"] is not None:
        t = objet(mesures["tokens"], ("id", "source", "perimetre", "entree", "sortie"))
        texte(t["id"]); texte(t["source"])
        if t["perimetre"] != "execution_exclusive":
            raise ValueError("Mesure exclusive attendue, sans enfants ni cumuls")
        entier(t["entree"]); entier(t["sortie"])
    if mesures["cout"] is not None:
        c = objet(mesures["cout"], ("montant", "nature", "devise", "source"))
        if (not isinstance(c["montant"], str) or not re.fullmatch(r"\d{1,18}(?:\.\d{1,9})?", c["montant"])
                or c["nature"] not in ("estime", "constate") or not isinstance(c["devise"], str) or not re.fullmatch(r"[A-Z]{3}", c["devise"])):
            raise ValueError("Cout : montant decimal, nature et devise attendus")
        texte(c["source"])
    if mesures["traces"] is not None:
        t = objet(mesures["traces"], ("couverture", "source"))
        if t["couverture"] not in ("non_verifiee", "partielle", "complete_declaree"):
            raise ValueError("Couverture de traces inconnue")
        texte(t["source"])
    if mesures["duree_observee"] is not None:
        d = objet(mesures["duree_observee"], ("secondes", "source", "nature"))
        if nombre(d["secondes"]) < 0 or d["nature"] != "murale":
            raise ValueError("Duree murale non negative attendue ; ce n'est pas un temps modele")
        texte(d["source"])


def resultats(racine, m):
    dossier = racine / "resultats"
    if not os.path.lexists(dossier):
        return {}
    info = dossier.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ValueError("Dossier de resultats ordinaire attendu")
    connus = {e["id"]: e for e in m["executions"]}
    trouves = {}
    for p in sorted(dossier.iterdir()):
        if p.name not in connus:
            raise ValueError("Execution non preparee dans les resultats : " + p.name)
        # lire() controle aussi le dossier de chaque resultat.
        brut = lire(racine, f"resultats/{p.name}/rapport.json")
        r = verifier_sceau(decoder(brut))
        objet(r, ("format", "donnees", "pieces", "declaration", "empreinte"))
        if type(r["format"]) is not int or r["format"] != 1:
            raise ValueError("Format de resultat attendu : 1")
        valider_resultat(r["donnees"], m, connus[p.name])
        verifier_pieces(p, r["pieces"])
        original = lire(p, r["declaration"]["copie"])
        if sha(original) != r["declaration"]["sha256"] or canon(decoder(original)) != canon(r["donnees"]):
            raise ValueError("Declaration originale modifiee")
        trouves[p.name] = r
    ids = [r["donnees"]["tokens"]["id"] for r in trouves.values() if r["donnees"].get("tokens") is not None]
    if len(ids) != len(set(ids)):
        raise ValueError("Identifiant de mesure reutilise entre executions")
    ids_natifs = [r["donnees"]["provenance"]["id_natif"] for r in trouves.values() if r["donnees"]["nature"] == "reelle"]
    if len(ids_natifs) != len(set(ids_natifs)):
        raise ValueError("Identifiant natif reutilise entre contextes")
    return trouves


def enregistrer(dossier, execution_id, fichier):
    racine, m = ouvrir_campagne(dossier)
    execution = next((e for e in m["executions"] if e["id"] == execution_id), None)
    if execution is None:
        raise ValueError("Execution absente du plan")
    fichier = Path(fichier).absolute()
    original = lire(fichier.parent.resolve(strict=True), fichier.name)
    r = decoder(original)
    valider_resultat(r, m, execution)
    precedents = resultats(racine, m)
    if execution_id in precedents:
        raise ValueError("Resultat deja enregistre ; premiere remise conservee")
    if r.get("tokens") and any(x["donnees"].get("tokens", {}).get("id") == r["tokens"]["id"] for x in precedents.values() if x["donnees"].get("tokens")):
        raise ValueError("Identifiant de mesure deja utilise")
    if r["nature"] == "reelle" and any(x["donnees"]["provenance"]["id_natif"] == r["provenance"]["id_natif"] for x in precedents.values()):
        raise ValueError("Identifiant natif deja utilise ; contexte distinct requis")
    pieces, octets = figer(Path(fichier).absolute().parent.resolve(strict=True), r["sorties"])
    parent = racine / "resultats"
    parent.mkdir(exist_ok=True)
    cible = parent / execution_id
    octets["declaration.json"] = original
    creer_dossier(cible, octets, "rapport.json", dict(format=1, donnees=r, pieces=pieces,
                                                   declaration=dict(copie="declaration.json", sha256=sha(original))))
    return cible


def controler(c, rapport, racine):
    if c["type"] == "revue":
        avis = rapport["donnees"]["revues"].get(c["id"])
        return dict(critere=c["id"], definition=c, methode="revue_attribuee", etat=avis["etat"] if avis else "non_verifie",
                    preuve=avis if avis else "Aucune revue fournie ; aucun verdict automatique")
    try:
        p = rapport["pieces"].get(c["fichier"])
        if p is None:
            raise ValueError("Sortie attendue non fournie")
        valeur = decoder(lire(racine, p["copie"]))
        for cle in c["chemin"]:
            if type(cle) is int and not isinstance(valeur, list) or isinstance(cle, str) and not isinstance(valeur, dict):
                raise ValueError("Structure du chemin JSON incompatible")
            valeur = valeur[cle]
        if c["type"] == "json_egal":
            satisfait = canon(valeur) == canon(c["attendu"])
        else:
            nombre(valeur)
            satisfait = c.get("minimum", -math.inf) <= valeur <= c.get("maximum", math.inf)
        preuve = dict(fichier=c["fichier"], sha256=p["sha256"], chemin=c["chemin"], valeur=valeur)
    except (ValueError, KeyError, IndexError, TypeError, UnicodeError) as exc:
        satisfait, preuve = False, "Controle impossible ou contrat non satisfait : " + str(exc)
    return dict(critere=c["id"], definition=c, methode=c["type"], etat="satisfait" if satisfait else "non_satisfait", preuve=preuve)


def fraction(n, d):
    return dict(numerateur=n, denominateur=d, taux=n / d if d else None)


def bilan(dossier):
    racine, m = ouvrir_campagne(dossier)
    rapports = resultats(racine, m)
    details, series = [], defaultdict(list)
    cas = {c["id"]: c for c in m["plan"]["cas"]}
    versions = {v["id"]: v for v in m["plan"]["versions"]}
    for e in m["executions"]:
        r = rapports.get(e["id"])
        d = dict(e, empreinte_execution=empreinte_execution(m, e), reglages_demandes=versions[e["version"]]["reglages_demandes"],
                 etat="preparee", issue="non_evaluee", criteres=[], mesures=None)
        if r is not None:
            donnees = r["donnees"]
            ecarts = list(donnees["ecarts"])
            if donnees["provenance"]["hote"] != m["plan"]["hote"]:
                ecarts.append("Hote different du plan")
            applique = donnees.get("reglages_appliques")
            demande = versions[e["version"]]["reglages_demandes"]
            if applique and demande and any(applique[k] != demande[k] for k in ("modele", "effort")):
                ecarts.append("Reglages appliques differents de la demande figee")
            d.update(etat="hors_protocole" if ecarts else donnees["etat"], etat_declare=donnees["etat"], ecarts=ecarts,
                     provenance=donnees["provenance"], mesures={k: donnees.get(k) for k in ("tokens", "cout", "traces", "reglages_appliques", "duree_observee")})
            d["criteres"] = [controler(c, r, racine / "resultats" / e["id"]) for c in cas[e["cas"]]["criteres"]]
            if d["etat"] == "terminee":
                indispensables = {c["id"] for c in cas[e["cas"]]["criteres"] if c["obligatoire"]}
                etats = [c["etat"] for c in d["criteres"] if c["critere"] in indispensables]
                d["issue"] = "echec" if "non_satisfait" in etats else "inconclusive" if "non_verifie" in etats else "succes"
        details.append(d)
        series[(e["cas"], e["version"])].append(d)

    def resumer(lignes):
        etats = Counter(x["etat"] for x in lignes)
        issues = Counter(x["issue"] for x in lignes)
        return dict(prevues=len(lignes), preparees=etats["preparee"], terminees=etats["terminee"], interrompues=etats["interrompue"],
                    hors_protocole=etats["hors_protocole"], enregistrees=len(lignes) - etats["preparee"],
                    evaluables=issues["succes"] + issues["echec"], inconclusives=issues["inconclusive"],
                    succes=issues["succes"], echecs=issues["echec"],
                    succes_sur_evaluables=fraction(issues["succes"], issues["succes"] + issues["echec"]),
                    succes_sur_prevues=fraction(issues["succes"], len(lignes)))

    groupes = []
    for (c, v), lignes in series.items():
        par_critere = []
        for crit in cas[c]["criteres"]:
            comptes = Counter()
            for ligne in lignes:
                observation = next((x for x in ligne["criteres"] if x["critere"] == crit["id"]), None)
                comptes[observation["etat"] if observation and ligne["etat"] == "terminee" else "non_evalue"] += 1
            par_critere.append(dict(id=crit["id"], type=crit["type"], obligatoire=crit["obligatoire"],
                                   comptes={k: comptes[k] for k in ("satisfait", "non_satisfait", "non_verifie", "non_evalue")}, prevues=len(lignes)))
        groupes.append(dict(cas=c, version=v, resume=resumer(lignes), criteres=par_critere))
    mesures = [x["mesures"] for x in details if x["mesures"] is not None]
    tokens = [x["tokens"] for x in mesures if x["tokens"] is not None]
    couts = defaultdict(list)
    for x in mesures:
        if x["cout"]:
            c = x["cout"]
            couts[(c["nature"], c["devise"])].append(Decimal(c["montant"]))
    with localcontext() as ctx:
        ctx.prec = 60
        groupes_couts = [dict(nature=k[0], devise=k[1], sous_total_connu=str(sum(v)), renseignees=len(v)) for k, v in sorted(couts.items())]
    couverture = dict(denominateur=len(mesures), tokens_renseignes=len(tokens), couts_renseignes=sum(len(v) for v in couts.values()),
                      reglages_renseignes=sum(x["reglages_appliques"] is not None for x in mesures),
                      traces_renseignees=sum(x["traces"] is not None for x in mesures),
                      durees_murales_renseignees=sum(x["duree_observee"] is not None for x in mesures))
    resume = resumer(details)
    resume["executees_reelles_declarees"] = len(rapports) if m["plan"]["nature"] == "reelle" else 0
    resume["observations_simulees"] = len(rapports) if m["plan"]["nature"] == "simulation" else 0
    return dict(format=1, campagne=m["plan"]["id"], nature=m["plan"]["nature"], hypothese=m["plan"]["hypothese"],
                hote_prevu=m["plan"]["hote"], empreinte_campagne=m["empreinte"],
                etat="partiel" if any(x["etat"] != "terminee" or x["issue"] == "inconclusive" for x in details) else "complet",
                resume=resume, series=groupes, executions=details, couverture_mesures=couverture,
                tokens_connus=dict(entree=sum(x["entree"] for x in tokens), sortie=sum(x["sortie"] for x in tokens)) if tokens else None,
                couts_connus=groupes_couts,
                limites=["Resultats et provenance declares par l'operateur, sans verification native ni lancement de modele.",
                         "Un taux sur les evaluables exclut les interruptions, inconnues et ecarts : lire tous les denominateurs.",
                         "Sous-totaux d'usage connus, sans conversion de devise, tarification ou gain economique deduit.",
                         "Durees murales fournies, pas des temps de calcul modele ; couverture de traces declaree.",
                         "Les controles lisent des donnees ; aucun script ou prototype fourni n'est execute."])


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commandes = parser.add_subparsers(dest="commande", required=True)
    p = commandes.add_parser("preparer")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--racine", type=Path, default=Path(".orka/evaluations"))
    e = commandes.add_parser("enregistrer")
    e.add_argument("--campagne", required=True, type=Path)
    e.add_argument("--execution", required=True)
    e.add_argument("--resultat", required=True, type=Path)
    b = commandes.add_parser("bilan")
    b.add_argument("--campagne", required=True, type=Path)
    b.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.commande == "preparer":
            dossier = preparer(args.plan, args.racine)
            sortie = dict(etat="preparee_non_lancee", dossier=str(dossier), bilan=bilan(dossier))
        elif args.commande == "enregistrer":
            dossier = enregistrer(args.campagne, args.execution, args.resultat)
            sortie = dict(etat="resultat_fourni_enregistre", dossier=str(dossier))
        else:
            sortie = bilan(args.campagne)
            if args.output:
                ecrire(args.output, sortie)
        print(json.dumps(sortie, ensure_ascii=False, allow_nan=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError) as exc:
        parser.exit(2, "Erreur : " + str(exc) + "\n")


if __name__ == "__main__":
    main()
