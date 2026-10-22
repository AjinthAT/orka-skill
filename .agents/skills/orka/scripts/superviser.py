#!/usr/bin/env python3
"""Registre transactionnel local. Ne lance ni modele ni agent et ne stoppe aucun processus."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import uuid

from preparer_agent import charger_json, configurer_sorties, empreinte_requete, nom_lancement, preparer, texte


SCHEMA = """
CREATE TABLE configuration (id INTEGER PRIMARY KEY CHECK(id=1), racine TEXT NOT NULL,
    capacite INTEGER NOT NULL CHECK(capacite>0), version INTEGER NOT NULL);
CREATE TABLE taches (mission TEXT NOT NULL, id TEXT NOT NULL, requete TEXT NOT NULL,
    fichier TEXT NOT NULL, acceptation TEXT NOT NULL, etat TEXT NOT NULL,
    maximum INTEGER NOT NULL, tentatives INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(mission,id));
CREATE TABLE dependances (mission TEXT NOT NULL, tache TEXT NOT NULL, amont TEXT NOT NULL,
    PRIMARY KEY(mission,tache,amont),
    FOREIGN KEY(mission,tache) REFERENCES taches(mission,id),
    FOREIGN KEY(mission,amont) REFERENCES taches(mission,id));
CREATE TABLE tentatives (id TEXT PRIMARY KEY, mission TEXT NOT NULL, tache TEXT NOT NULL,
    numero INTEGER NOT NULL, requete TEXT NOT NULL, fichier TEXT NOT NULL,
    active INTEGER NOT NULL, phase TEXT NOT NULL, agent TEXT, appliques TEXT,
    activite REAL NOT NULL, observations TEXT, empreinte TEXT, entrees TEXT,
    UNIQUE(mission,tache,numero), FOREIGN KEY(mission,tache) REFERENCES taches(mission,id));
CREATE UNIQUE INDEX sortie_active ON tentatives(fichier) WHERE active=1;
CREATE UNIQUE INDEX tache_active ON tentatives(mission,tache) WHERE active=1;
CREATE UNIQUE INDEX agent_actif ON tentatives(agent) WHERE active=1 AND agent IS NOT NULL;
CREATE TABLE evenements (id INTEGER PRIMARY KEY, date REAL NOT NULL, mission TEXT,
    tache TEXT, tentative TEXT, type TEXT NOT NULL, details TEXT NOT NULL);
"""


def entier_positif(value, champ):
    if type(value) is not int or value < 1:
        raise ValueError(f"{champ} doit etre un entier positif")
    return value


def empreinte_fichier(path):
    resultat = hashlib.sha256()
    with Path(path).open("rb") as fichier:
        for bloc in iter(lambda: fichier.read(1024 * 1024), b""):
            resultat.update(bloc)
    return resultat.hexdigest()


class Superviseur:
    @staticmethod
    def initialiser(base, racine, capacite=3):
        entier_positif(capacite, "capacite")
        racine = Path(racine).resolve()
        if not racine.is_dir():
            raise ValueError("La racine doit etre un dossier existant")
        base = Path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        with base.open("xb"):
            pass
        connexion = sqlite3.connect(str(base))
        try:
            connexion.executescript(SCHEMA)
            connexion.execute("INSERT INTO configuration VALUES (1,?,?,2)", (str(racine), capacite))
            connexion.commit()
        finally:
            connexion.close()

    def __init__(self, base, horloge=time.time):
        if not Path(base).is_file():
            raise ValueError("Base absente ; initialiser explicitement le registre")
        self.db = sqlite3.connect(str(base), timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.horloge = horloge
        self.base = Path(base).resolve()
        config = self.db.execute("SELECT * FROM configuration WHERE id=1").fetchone()
        if config is None or config["version"] != 2:
            self.db.close()
            raise ValueError("Version du registre incompatible ; pour une base v1, executer migrer")
        self.racine = Path(config["racine"])
        self.capacite = config["capacite"]

    @staticmethod
    def migrer(base):
        base = Path(base).resolve()
        if not base.is_file():
            raise ValueError("Base absente ; aucune migration possible")
        connexion = sqlite3.connect(str(base), isolation_level=None, timeout=5)
        try:
            connexion.execute("BEGIN IMMEDIATE")
            config = connexion.execute("SELECT version FROM configuration WHERE id=1").fetchone()
            if config and config[0] == 2:
                connexion.commit()
                return {"etat": "registre_deja_v2", "sauvegarde": None}
            if config is None or config[0] != 1:
                raise ValueError("Version du registre incompatible")
            sauvegarde = base.with_name(base.name + ".avant-v2-" + uuid.uuid4().hex + ".sqlite")
            with sauvegarde.open("xb"):
                pass
            # Une seconde connexion peut lire sous le verrou d'ecriture reserve.
            # L'API backup inclut les donnees validees, meme en mode WAL.
            lecteur = sqlite3.connect(str(base))
            copie = sqlite3.connect(str(sauvegarde))
            try:
                lecteur.backup(copie)
            finally:
                copie.close()
                lecteur.close()
            connexion.execute("ALTER TABLE tentatives ADD COLUMN entrees TEXT")
            connexion.execute("UPDATE configuration SET version=2 WHERE id=1")
            connexion.execute("INSERT INTO evenements(date,type,details) VALUES (?,?,?)",
                              (time.time(), "migration_v2", json.dumps({"sauvegarde": str(sauvegarde)})))
            connexion.commit()
            return {"etat": "registre_migre_v2", "sauvegarde": str(sauvegarde)}
        except Exception:
            connexion.rollback()
            raise
        finally:
            connexion.close()

    def fermer(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except Exception:
            self.db.rollback()
            raise
        else:
            self.db.commit()

    def chemin(self, fichier):
        path = Path(fichier)
        path = (path if path.is_absolute() else self.racine / path).resolve()
        try:
            path.relative_to(self.racine)
        except ValueError:
            raise ValueError("Le livrable doit rester dans la racine du registre") from None
        if str(path) in {str(self.base), *(str(self.base) + suffixe for suffixe in ("-journal", "-wal", "-shm"))}:
            raise ValueError("Le registre et ses fichiers techniques ne sont pas des livrables")
        if path.is_dir():
            raise ValueError("Le livrable doit designer un fichier")
        return str(path)

    def tache(self, mission, tache):
        row = self.db.execute("SELECT * FROM taches WHERE mission=? AND id=?", (mission, tache)).fetchone()
        if row is None:
            raise ValueError("Tache inconnue")
        return row

    def execution(self, identifiant, active=True):
        row = self.db.execute("SELECT * FROM tentatives WHERE id=?", (identifiant,)).fetchone()
        if row is None or (active and not row["active"]):
            raise ValueError("Tentative absente ou deja liberee")
        return row

    def evenement(self, type_, mission, tache, tentative=None, **details):
        self.db.execute("INSERT INTO evenements(date,mission,tache,tentative,type,details) VALUES (?,?,?,?,?,?)",
                        (self.horloge(), mission, tache, tentative, type_, json.dumps(details, ensure_ascii=False)))

    def ajouter(self, mandat, fichier, dependances=(), maximum=2):
        entier_positif(maximum, "maximum")
        if not isinstance(mandat, dict):
            raise ValueError("Le mandat doit etre un objet JSON")
        if not isinstance(dependances, (list, tuple)):
            raise ValueError("Les dependances doivent etre une liste d'identifiants")
        dependances = [texte(amont, "dependance") for amont in dependances]
        fichier = self.chemin(texte(fichier, "fichier"))
        if self.chemin(texte(mandat.get("sortie"), "sortie")) != fichier:
            raise ValueError("Le mandat doit designer le fichier de sortie reserve")
        if mandat.get("tentative", 1) != 1 or type(mandat.get("tentative", 1)) is not int:
            raise ValueError("Le registre attribue les tentatives ; enregistrer la tache avec tentative 1")
        requete = preparer(dict(mandat, sortie=fichier))
        requete["criteres_attendus"] = {f"C-{i:02d}": valeur.strip() for i, valeur in enumerate(mandat["criteres"], 1)}
        mission, tache = requete["mission_id"], requete["tache_id"]
        with self.transaction():
            for amont in dependances:
                if amont == tache:
                    raise ValueError("Une tache ne peut pas dependre d'elle-meme")
                self.tache(mission, amont)
            self.db.execute("INSERT INTO taches VALUES (?,?,?,?,?,'a_faire',?,0)",
                            (mission, tache, json.dumps(requete, ensure_ascii=False), fichier,
                             mandat["acceptation"].strip(), maximum))
            self.db.executemany("INSERT INTO dependances VALUES (?,?,?)",
                                [(mission, tache, amont) for amont in set(dependances)])
            self.evenement("tache_ajoutee", mission, tache)

    def reference_valide(self, tache, parcours=None, cache=None):
        if tache["etat"] != "terminee":
            return False
        parcours = set() if parcours is None else set(parcours)
        cle = (tache["mission"], tache["id"])
        if cle in parcours:
            return False
        cache = {} if cache is None else cache
        if cle in cache:
            return cache[cle]
        parcours.add(cle)
        row = self.db.execute("SELECT * FROM tentatives WHERE mission=? AND tache=? ORDER BY numero DESC LIMIT 1",
                              (tache["mission"], tache["id"])).fetchone()
        active = self.db.execute("SELECT 1 FROM tentatives WHERE fichier=? AND active=1", (tache["fichier"],)).fetchone()
        try:
            valide = (row is not None and not active and self.chemin(tache["fichier"]) == tache["fichier"]
                    and empreinte_fichier(tache["fichier"]) == row["empreinte"]
                    and not self.entrees_invalides(tache["mission"], tache["id"], row["entrees"], parcours, cache))
        except (OSError, ValueError):
            valide = False
        cache[cle] = valide
        return valide

    def manquantes(self, mission, tache):
        amonts = self.db.execute("SELECT amont FROM dependances WHERE mission=? AND tache=?", (mission, tache))
        cache = {}
        return [row["amont"] for row in amonts if not self.reference_valide(self.tache(mission, row["amont"]), cache=cache)]

    def entrees_actuelles(self, mission, tache):
        rows = self.db.execute("SELECT d.amont,t.id,t.empreinte FROM dependances d JOIN tentatives t "
                               "ON t.mission=d.mission AND t.tache=d.amont "
                               "WHERE d.mission=? AND d.tache=? AND t.numero=(SELECT MAX(numero) FROM tentatives "
                               "WHERE mission=d.mission AND tache=d.amont) ORDER BY d.amont", (mission, tache))
        return {row["amont"]: {"execution_id": row["id"], "empreinte": row["empreinte"]} for row in rows}

    def entrees_invalides(self, mission, tache, entrees, parcours=None, cache=None):
        amonts = [r[0] for r in self.db.execute("SELECT amont FROM dependances WHERE mission=? AND tache=? ORDER BY amont", (mission, tache))]
        # Une base v1 n'enregistrait pas ces versions : ne pas les reconstituer.
        if entrees is None:
            return amonts
        attendues = json.loads(entrees)
        actuelles = self.entrees_actuelles(mission, tache)
        cache = {} if cache is None else cache
        invalides = set(amonts) ^ set(attendues)
        for amont in amonts:
            if (attendues.get(amont) != actuelles.get(amont)
                    or not self.reference_valide(self.tache(mission, amont), parcours, cache)):
                invalides.add(amont)
        return sorted(invalides)

    def dependants(self, mission, tache):
        rows = self.db.execute("WITH RECURSIVE aval(id) AS (SELECT tache FROM dependances WHERE mission=? AND amont=? "
                               "UNION SELECT d.tache FROM dependances d JOIN aval a ON d.amont=a.id WHERE d.mission=?) "
                               "SELECT id FROM aval WHERE id<>? ORDER BY id", (mission, tache, mission, tache))
        return [r[0] for r in rows]

    def reserver(self, mission, tache):
        with self.transaction():
            row = self.tache(mission, tache)
            if row["etat"] != "a_faire":
                raise ValueError("La tache n'est pas prete a etre reservee")
            if self.manquantes(mission, tache):
                raise ValueError("Dependances incompletes ou versions a reexaminer")
            if row["tentatives"] >= row["maximum"]:
                raise ValueError("Limite de tentatives atteinte")
            if self.db.execute("SELECT COUNT(*) FROM tentatives WHERE active=1").fetchone()[0] >= self.capacite:
                raise ValueError("Capacite globale du registre atteinte")
            if self.db.execute("SELECT 1 FROM tentatives WHERE fichier=? AND active=1", (row["fichier"],)).fetchone():
                raise ValueError("Fichier deja reserve par une autre tentative")
            requete = deepcopy(json.loads(row["requete"]))
            entrees = self.entrees_actuelles(mission, tache)
            requete["entrees_verifiees"] = entrees
            numero = row["tentatives"] + 1
            requete["tentative"] = numero
            if numero > 1:
                evenement = self.db.execute("SELECT details FROM evenements WHERE mission=? AND tache=? AND type='reprise_preparee' ORDER BY id DESC LIMIT 1", (mission, tache)).fetchone()
                precedente = self.db.execute("SELECT observations,empreinte FROM tentatives WHERE mission=? AND tache=? ORDER BY numero DESC LIMIT 1", (mission, tache)).fetchone()
                contexte = {
                    "motif": json.loads(evenement["details"])["motif"],
                    "observations_precedentes": json.loads(precedente["observations"]) if precedente["observations"] else None,
                    "empreinte_precedente_a_verifier": precedente["empreinte"],
                }
                requete["contexte_reprise"] = contexte
                requete["parametres_demandes"]["message"] += ("\n\n# Contexte de la nouvelle tentative\n"
                    "La tentative precedente a ete liberee. Traiter le constat dans le mandat existant ; verifier les versions avant reutilisation.\n"
                    + json.dumps(contexte, ensure_ascii=False, indent=2))
            if entrees:
                requete["parametres_demandes"]["message"] += ("\n\n# Versions des entrees a utiliser\n"
                    + json.dumps(entrees, ensure_ascii=False, indent=2))
            requete["empreinte_prompt"] = hashlib.sha256(requete["parametres_demandes"]["message"].encode()).hexdigest()
            requete["parametres_demandes"]["task_name"] = nom_lancement(mission, tache, requete["role"], numero)
            requete["empreinte_requete"] = empreinte_requete(requete["parametres_demandes"])
            identifiant = uuid.uuid4().hex
            self.db.execute("INSERT INTO tentatives(id,mission,tache,numero,requete,fichier,active,phase,activite,entrees) VALUES (?,?,?,?,?,?,1,'reservee',?,?)",
                            (identifiant, mission, tache, numero, json.dumps(requete, ensure_ascii=False), row["fichier"], self.horloge(), json.dumps(entrees)))
            self.db.execute("UPDATE taches SET etat='en_cours',tentatives=? WHERE mission=? AND id=?", (numero, mission, tache))
            self.evenement("reservation", mission, tache, identifiant, numero=numero)
            return {"execution_id": identifiant, "phase": "reservee", "requete": requete}

    def requete(self, identifiant):
        row = self.execution(identifiant, active=False)
        return {"execution_id": identifiant, "phase": row["phase"], "active": bool(row["active"]),
                "agent": row["agent"], "requete": json.loads(row["requete"])}

    def attacher(self, identifiant, agent, appliques=None):
        agent = texte(agent, "agent")
        if appliques is not None and (not isinstance(appliques, dict) or set(appliques) != {"model", "reasoning_effort"}
                                      or not all(isinstance(v, str) and v.strip() for v in appliques.values())):
            raise ValueError("Parametres observes attendus : model et reasoning_effort")
        with self.transaction():
            row = self.execution(identifiant)
            if row["phase"] != "reservee":
                raise ValueError("Un agent est deja rattache a cette tentative")
            self.db.execute("UPDATE tentatives SET agent=?,phase='lance',appliques=?,activite=? WHERE id=?",
                            (agent, json.dumps(appliques) if appliques else None, self.horloge(), identifiant))
            self.evenement("agent_rattache", row["mission"], row["tache"], identifiant, agent=agent)

    def battement(self, identifiant):
        with self.transaction():
            self.execution(identifiant)
            self.db.execute("UPDATE tentatives SET activite=? WHERE id=?", (self.horloge(), identifiant))

    def soumettre(self, identifiant, observations):
        with self.transaction():
            row = self.execution(identifiant)
            if row["phase"] != "lance":
                raise ValueError("Un resultat exige un lancement rattache et aucune soumission precedente")
            base = json.loads(self.tache(row["mission"], row["tache"])["requete"])
            attendus = base["criteres_attendus"]
            if not isinstance(observations, dict) or set(observations) != set(attendus):
                raise ValueError("Les observations doivent couvrir exactement les criteres attendus")
            for item in observations.values():
                if not isinstance(item, dict) or set(item) != {"etat", "preuve"} or item["etat"] not in ("satisfait", "non_satisfait", "non_verifie"):
                    raise ValueError("Observation attendue : etat et preuve")
                texte(item["preuve"], "preuve ou constat")
            if self.chemin(row["fichier"]) != row["fichier"]:
                raise ValueError("Le chemin du livrable a change")
            empreinte = empreinte_fichier(row["fichier"])
            self.db.execute("UPDATE tentatives SET observations=?,empreinte=?,phase='resultat_recu',activite=? WHERE id=?",
                            (json.dumps(observations, ensure_ascii=False), empreinte, self.horloge(), identifiant))
            self.db.execute("UPDATE taches SET etat='a_verifier' WHERE mission=? AND id=?", (row["mission"], row["tache"]))
            self.evenement("resultat_recu", row["mission"], row["tache"], identifiant, empreinte=empreinte)

    def liberer(self, identifiant, preuve_arret):
        preuve_arret = texte(preuve_arret, "preuve_arret")
        with self.transaction():
            row = self.execution(identifiant)
            self.db.execute("UPDATE tentatives SET active=0,phase='liberee',activite=? WHERE id=?", (self.horloge(), identifiant))
            if row["observations"] is None:
                self.db.execute("UPDATE taches SET etat='bloquee' WHERE mission=? AND id=?", (row["mission"], row["tache"]))
            self.evenement("liberation_confirmee", row["mission"], row["tache"], identifiant, preuve_arret=preuve_arret)

    def accepter(self, mission, tache, validateur):
        with self.transaction():
            row = self.tache(mission, tache)
            if row["etat"] != "a_verifier" or validateur != row["acceptation"]:
                raise ValueError("Etat ou responsable d'acceptation incorrect")
            tentative = self.db.execute("SELECT * FROM tentatives WHERE mission=? AND tache=? ORDER BY numero DESC LIMIT 1", (mission, tache)).fetchone()
            if self.db.execute("SELECT 1 FROM tentatives WHERE fichier=? AND active=1", (row["fichier"],)).fetchone():
                raise ValueError("Le fichier a encore un redacteur actif")
            observations = json.loads(tentative["observations"])
            if any(item["etat"] != "satisfait" for item in observations.values()):
                raise ValueError("Un critere indispensable n'est pas satisfait")
            if (self.entrees_invalides(mission, tache, tentative["entrees"]) or self.chemin(row["fichier"]) != row["fichier"]
                    or empreinte_fichier(row["fichier"]) != tentative["empreinte"]):
                raise ValueError("Version du resultat ou des dependances a reexaminer")
            self.db.execute("UPDATE taches SET etat='terminee' WHERE mission=? AND id=?", (mission, tache))
            self.evenement("acceptation", mission, tache, tentative["id"], validateur=validateur)

    def reexaminer(self, mission, tache, motif, validateur):
        motif = texte(motif, "motif")
        with self.transaction():
            row = self.tache(mission, tache)
            if row["etat"] != "terminee" or validateur != row["acceptation"]:
                raise ValueError("Etat ou responsable de reexamen incorrect")
            if self.db.execute("SELECT 1 FROM tentatives WHERE fichier=? AND active=1", (row["fichier"],)).fetchone():
                raise ValueError("Confirmer la fin du redacteur avant reexamen")
            affectees = self.dependants(mission, tache)
            self.db.execute("UPDATE taches SET etat='a_reexaminer' WHERE mission=? AND id=?", (mission, tache))
            self.evenement("reexamen_demande", mission, tache, motif=motif, validateur=validateur, dependants=affectees)
            return {"etat": "a_reexaminer", "dependants_a_reexaminer": affectees}

    def reprendre(self, mission, tache, motif):
        motif = texte(motif, "motif")
        with self.transaction():
            row = self.tache(mission, tache)
            if row["etat"] not in ("bloquee", "a_verifier", "a_reexaminer"):
                raise ValueError("Seule une tache bloquee ou a corriger peut etre reprise")
            if self.db.execute("SELECT 1 FROM tentatives WHERE mission=? AND tache=? AND active=1", (mission, tache)).fetchone():
                raise ValueError("Confirmer la fin de l'ancien redacteur avant reprise")
            if row["tentatives"] >= row["maximum"]:
                raise ValueError("Limite de tentatives atteinte")
            self.db.execute("UPDATE taches SET etat='a_faire' WHERE mission=? AND id=?", (mission, tache))
            self.evenement("reprise_preparee", mission, tache, motif=motif)

    def etat(self, mission=None):
        occupation = self.db.execute("SELECT COUNT(*) FROM tentatives WHERE active=1").fetchone()[0]
        rows = self.db.execute("SELECT * FROM taches" + (" WHERE mission=?" if mission else "") + " ORDER BY mission,id", (mission,) if mission else ())
        taches = []
        for row in rows:
            item = {k: row[k] for k in ("mission", "id", "etat", "tentatives", "maximum", "fichier")}
            demande = json.loads(row["requete"])
            item["profil_demande"] = demande["profil"]
            item["modele_demande"] = demande["parametres_demandes"]["model"]
            item["effort_demande"] = demande["parametres_demandes"]["reasoning_effort"]
            dernier = self.db.execute("SELECT id,numero,phase,agent,appliques FROM tentatives WHERE mission=? AND tache=? ORDER BY numero DESC LIMIT 1", (row["mission"], row["id"])).fetchone()
            item["derniere_execution"] = ({k: dernier[k] for k in ("id", "numero", "phase", "agent")} if dernier else None)
            item["parametres_appliques_declares"] = json.loads(dernier["appliques"]) if dernier and dernier["appliques"] else None
            item["dependances_a_reexaminer"] = self.manquantes(row["mission"], row["id"])
            tentative = self.db.execute("SELECT entrees FROM tentatives WHERE mission=? AND tache=? ORDER BY numero DESC LIMIT 1", (row["mission"], row["id"])).fetchone()
            item["entrees_utilisees"] = json.loads(tentative["entrees"]) if tentative and tentative["entrees"] is not None else None
            item["entrees_a_reexaminer"] = self.entrees_invalides(row["mission"], row["id"], tentative["entrees"]) if tentative else []
            item["validite"] = ("valide" if self.reference_valide(row) else "a_reexaminer") if row["etat"] == "terminee" else row["etat"]
            fichier_reserve = self.db.execute("SELECT 1 FROM tentatives WHERE fichier=? AND active=1", (row["fichier"],)).fetchone()
            item["prete"] = (row["etat"] == "a_faire" and not item["dependances_a_reexaminer"]
                             and occupation < self.capacite and not fichier_reserve and row["tentatives"] < row["maximum"])
            taches.append(item)
        actives = [dict(row) for row in self.db.execute("SELECT id,mission,tache,numero,phase,agent,activite FROM tentatives WHERE active=1")]
        return {"capacite": self.capacite, "actives": actives, "taches": taches}

    def alertes(self, delai):
        entier_positif(delai, "delai")
        return [dict(row) for row in self.db.execute("SELECT id,mission,tache,phase,agent,activite FROM tentatives WHERE active=1 AND activite<=?", (self.horloge() - delai,))]

    def journal(self):
        return [dict(row) for row in self.db.execute("SELECT * FROM evenements ORDER BY id")]


def main():
    configurer_sorties()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    commandes = parser.add_subparsers(dest="commande", required=True)
    init = commandes.add_parser("initialiser")
    init.add_argument("--racine", type=Path, required=True)
    init.add_argument("--capacite", type=int, default=3)
    commandes.add_parser("migrer")
    ajouter = commandes.add_parser("ajouter")
    ajouter.add_argument("--mandat", type=Path, required=True)
    ajouter.add_argument("--fichier", required=True)
    ajouter.add_argument("--dependance", action="append", default=[])
    ajouter.add_argument("--maximum", type=int, default=2)
    for nom in ("reserver", "accepter", "reprendre", "reexaminer"):
        commande = commandes.add_parser(nom)
        commande.add_argument("--mission", required=True)
        commande.add_argument("--tache", required=True)
        if nom in ("accepter", "reexaminer"):
            commande.add_argument("--validateur", required=True)
        if nom in ("reprendre", "reexaminer"):
            commande.add_argument("--motif", required=True)
    for nom in ("attacher", "battement", "soumettre", "liberer", "requete"):
        commande = commandes.add_parser(nom)
        commande.add_argument("--execution", required=True)
        if nom == "attacher":
            commande.add_argument("--agent", required=True)
            commande.add_argument("--appliques", type=Path)
        if nom == "soumettre":
            commande.add_argument("--observations", type=Path, required=True)
        if nom == "liberer":
            commande.add_argument("--preuve-arret", required=True)
    etat = commandes.add_parser("etat")
    etat.add_argument("--mission")
    alertes = commandes.add_parser("alertes")
    alertes.add_argument("--delai", type=int, required=True)
    commandes.add_parser("journal")
    args = parser.parse_args()
    sup = None
    try:
        if args.commande == "initialiser":
            Superviseur.initialiser(args.base, args.racine, args.capacite)
            resultat = {"etat": "registre_initialise"}
        elif args.commande == "migrer":
            resultat = Superviseur.migrer(args.base)
        else:
            sup = Superviseur(args.base)
            if args.commande == "ajouter":
                sup.ajouter(charger_json(args.mandat), args.fichier, args.dependance, args.maximum)
                resultat = {"etat": "tache_ajoutee"}
            elif args.commande == "reserver":
                resultat = sup.reserver(args.mission, args.tache)
            elif args.commande == "attacher":
                sup.attacher(args.execution, args.agent, charger_json(args.appliques) if args.appliques else None)
                resultat = {"etat": "agent_rattache"}
            elif args.commande == "requete":
                resultat = sup.requete(args.execution)
            elif args.commande == "battement":
                sup.battement(args.execution)
                resultat = {"etat": "activite_enregistree"}
            elif args.commande == "soumettre":
                sup.soumettre(args.execution, charger_json(args.observations))
                resultat = {"etat": "resultat_a_verifier"}
            elif args.commande == "liberer":
                sup.liberer(args.execution, args.preuve_arret)
                resultat = {"etat": "reservation_liberee"}
            elif args.commande == "accepter":
                sup.accepter(args.mission, args.tache, args.validateur)
                resultat = {"etat": "tache_terminee"}
            elif args.commande == "reprendre":
                sup.reprendre(args.mission, args.tache, args.motif)
                resultat = {"etat": "reprise_preparee"}
            elif args.commande == "reexaminer":
                resultat = sup.reexaminer(args.mission, args.tache, args.motif, args.validateur)
            elif args.commande == "etat":
                resultat = sup.etat(args.mission)
            elif args.commande == "alertes":
                resultat = sup.alertes(args.delai)
            else:
                resultat = sup.journal()
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(2, f"Erreur : {exc}\n")
    finally:
        if sup:
            sup.fermer()


if __name__ == "__main__":
    main()
