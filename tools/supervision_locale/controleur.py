"""Boucle AUT-02A : tâches dans le registre v2, processus dans des reçus corrélés."""

import csv
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import threading
import time

from .processus import ProcessusFixes
from .stockage import (ajouter, demarrage_machine, echeance_comparable, ecrire, empreinte,
                       evenements, lire, verrou, verifier_plateforme)


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".agents/skills/orka/scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    from superviser import Superviseur
finally:
    sys.path.pop(0)

MISSION = "AUT-02A"
INCIDENTS = ("aucun", "erreur-permanente", "epuisement", "sortie-absente",
             "mauvais-total", "mauvais-type", "silence", "retour-tardif")


@contextmanager
def _sigint_differe():
    """Ne pas interrompre un arrêt borné ; aucun I/O dans le gestionnaire."""
    interruption = {"recue": False}

    def memoriser(numero, frame):
        interruption["recue"] = True

    ancien, installe = None, False
    if threading.current_thread() is threading.main_thread():
        ancien = signal.getsignal(signal.SIGINT)
        if ancien is not None and ancien != signal.SIG_IGN:
            signal.signal(signal.SIGINT, memoriser)
            installe = True
    try:
        yield interruption
    finally:
        if installe:
            signal.signal(signal.SIGINT, ancien)


def codes_sources():
    fichiers = [*sorted(Path(__file__).parent.glob("*.py")), SCRIPTS / "superviser.py"]
    return {str(f.relative_to(ROOT)): empreinte(f) for f in fichiers}


def creer(destination, incident="aucun", reprise=True, maximum=2, delai=2):
    """Créer explicitement un essai neuf ; ne jamais remettre une mission à zéro."""
    verifier_plateforme()
    if incident not in INCIDENTS or type(reprise) is not bool or type(maximum) is not int or maximum not in (1, 2):
        raise ValueError("Politique de recette invalide")
    if type(delai) not in (float, int) or not math.isfinite(delai) or not .1 <= delai <= 30:
        raise ValueError("Délai attendu entre 0.1 et 30 secondes")
    racine = Path(destination).absolute()
    racine.mkdir(parents=True, exist_ok=False)
    racine = racine.resolve()
    (racine / "executions").mkdir()
    (racine / "sorties").mkdir()
    (racine / "entree.csv").write_text("montant\n45\n80\n-10\n", encoding="utf-8")
    Superviseur.initialiser(racine / "registre.sqlite", racine, capacite=1)
    reg = Superviseur(racine / "registre.sqlite")
    try:
        for tache, sortie, dependances in (("T1", "total.json", []), ("T2", "bilan.json", ["T1"])):
            mandat = {"mission_id": MISSION, "tache_id": tache, "role": "redacteur",
                      "objectif": "Recette logicielle hors ligne : " + tache,
                      "contexte": ["Données fictives, programmes fixes, aucun modèle."],
                      "entrees": ["entree.csv" if tache == "T1" else "sorties/total.json"],
                      "sortie": str(racine / "sorties" / sortie),
                      "criteres": ["Résultat recalculé, types et preuves conformes au scénario."],
                      "acceptation": "verificateur-deterministe", "outils_autorises": [],
                      "limites": ["Pas de réseau, modèle, descendant ou effet extérieur dans ce programme fixe."],
                      "mode": "production"}
            reg.ajouter(mandat, mandat["sortie"], dependances, maximum if tache == "T1" else 1)
        config = {"version": 1, "mission": MISSION, "racine": str(racine), "incident": incident,
                  "reprise_autorisee": reprise, "maximum_T1": maximum, "delai": delai,
                  "source_sha256": empreinte(racine / "entree.csv"), "codes": codes_sources(),
                  "mandats": {t: hashlib.sha256(reg.tache(MISSION, t)["requete"].encode()).hexdigest()
                              for t in ("T1", "T2")}}
        ecrire(racine / "mission.json", config)
        (racine / "mission.sha256").write_text(empreinte(racine / "mission.json") + "\n", encoding="ascii")
        ecrire(racine / "controle.json", {"suspendue": False})
    finally:
        reg.fermer()
    return racine


class Controleur:
    def __init__(self, destination, point_controle=None):
        self.racine = Path(destination).resolve()
        self.point_controle = point_controle or (lambda point: None)
        self.adaptateur = ProcessusFixes()
        self.reg = None

    def log(self, type_, **details):
        ajouter(self.racine / "controleur.jsonl", dict(type=type_, date=time.time(),
                type_execution="processus_logiciel_fixe", appels_modeles=0, **details))

    def configuration(self):
        self.verifier_verrou()
        for nom in ("executions", "sorties", "registre.sqlite", "mission.json", "mission.sha256",
                    "controle.json", "entree.csv", "controleur.jsonl"):
            path = self.racine / nom
            if path.resolve() != path:
                raise ValueError("Chemin de recette déplacé ou lien symbolique : arrêt")
        if empreinte(self.racine / "mission.json") != (self.racine / "mission.sha256").read_text().strip():
            raise ValueError("Mandat de recette modifié : aucun lancement")
        config = lire(self.racine / "mission.json")
        if (config["version"] != 1 or config["mission"] != MISSION
                or config["racine"] != str(self.racine) or config["codes"] != codes_sources()
                or config["incident"] not in INCIDENTS):
            raise ValueError("Configuration, code ou racine incompatible ; requalification nécessaire")
        evenements(self.racine / "controleur.jsonl")  # Refuser aussi un journal incomplet.
        if self.reg.racine != self.racine or self.reg.capacite != 1:
            raise ValueError("Base ou capacité incompatible")
        if len(self.reg.etat()["taches"]) != 2:
            raise ValueError("Graphe de recette modifié")
        if self.reg.dependants(MISSION, "T1") != ["T2"] or self.reg.dependants(MISSION, "T2"):
            raise ValueError("Dépendances de recette modifiées")
        for tache in ("T1", "T2"):
            row = self.reg.tache(MISSION, tache)
            if hashlib.sha256(row["requete"].encode()).hexdigest() != config["mandats"][tache]:
                raise ValueError("Mandat du registre modifié")
            if row["maximum"] != (config["maximum_T1"] if tache == "T1" else 1):
                raise ValueError("Limite du registre modifiée")
        return config

    def entrees_valides(self):
        config = self.configuration()
        if empreinte(self.racine / "entree.csv") != config["source_sha256"]:
            raise ValueError("Entrée source modifiée : réexamen nécessaire")
        if lire(self.racine / "controle.json")["suspendue"]:
            raise ValueError("Mission suspendue")
        return config

    def dossier(self, execution):
        path = self.racine / "executions" / execution
        if path.resolve() != path:
            raise ValueError("Dossier de tentative déplacé : arrêt")
        return path

    def preparer(self, tache):
        config = self.entrees_valides()
        if self.reg.tache(MISSION, tache)["tentatives"] and not self.reprise_autorisee(tache):
            raise ValueError("Nouvelle tentative non autorisée")
        allocation = self.reg.reserver(MISSION, tache)
        execution = allocation["execution_id"]
        self.point_controle("reservee")
        dossier = self.dossier(execution)
        dossier.mkdir()
        row = self.reg.execution(execution)
        source = self.racine / ("entree.csv" if tache == "T1" else "sorties/total.json")
        entree = dossier / ("entree.csv" if tache == "T1" else "amont.json")
        contenu = source.read_bytes()
        entree.write_bytes(contenu)
        attendue = (config["source_sha256"] if tache == "T1"
                    else allocation["requete"]["entrees_verifiees"]["T1"]["empreinte"])
        if empreinte(entree) != attendue:
            raise ValueError("Entrée changée pendant la préparation")
        ecrire(dossier / "requete.json", {
            "execution_id": execution, "tache": tache, "numero": row["numero"],
            "incident": config["incident"], "source_sha256": attendue,
            "requete_registre_sha256": allocation["requete"]["empreinte_requete"],
            "demarrage_machine": demarrage_machine(),
            "echeance_monotone": time.monotonic() + config["delai"]})
        self.entrees_valides()
        self.log("intention_lancement", execution_id=execution, numero=row["numero"], tache=tache,
                 requete_sha256=empreinte(dossier / "requete.json"))
        self.point_controle("intention")
        pid = self.adaptateur.launch(dossier)
        self.point_controle("lancee")
        self.log("processus_cree", execution_id=execution, pid=pid)
        return execution

    def verifier_resultat(self, execution):
        """Recalcul indépendant du résultat logiciel ; aucune confiance dans son code 0."""
        self.entrees_valides()
        row = self.reg.execution(execution, active=False)
        dossier = self.dossier(execution)
        spec = lire(dossier / "requete.json")
        if self.reg.entrees_invalides(MISSION, row["tache"], row["entrees"]):
            raise ValueError("Dépendance modifiée : réexamen nécessaire")
        if row["tache"] == "T1":
            with (self.racine / "entree.csv").open(encoding="utf-8", newline="") as flux:
                total = sum(int(ligne["montant"]) for ligne in csv.DictReader(flux))
            attendue = {"total_net": total}
            entree = dossier / "entree.csv"
        else:
            # La sortie amont doit rester acceptée et valide dans le registre.
            if not self.reg.reference_valide(self.reg.tache(MISSION, "T1")):
                raise ValueError("T1 non acceptée ou périmée")
            total = json.loads((self.racine / "sorties/total.json").read_text())["total_net"]
            attendue = {"total_net": total, "source_sha256": empreinte(self.racine / "sorties/total.json"),
                        "bilan": f"Total net vérifié : {total}."}
            entree = dossier / "amont.json"
        if empreinte(entree) != spec["source_sha256"]:
            raise ValueError("Copie d'entrée modifiée")
        resultat = lire(dossier / "resultat.json")
        if (type(resultat) is not dict or resultat != attendue or type(resultat.get("total_net")) is not int
                or set(resultat) != set(attendue)):
            raise ValueError("Résultat métier incorrect ou type invalide")
        return {"etat": "satisfait", "preuve": "Recalcul indépendant et types vérifiés ; SHA256 "
                + empreinte(dossier / "resultat.json")}

    def traiter(self, execution):
        dossier = self.dossier(execution)
        if not (dossier / "requete.json").exists():
            self.log("lancement_inconnu", execution_id=execution)
            return False
        spec = lire(dossier / "requete.json")
        row = self.reg.execution(execution)
        intentions = [e for e in evenements(self.racine / "controleur.jsonl")
                      if e["type"] == "intention_lancement" and e["execution_id"] == execution]
        requete = self.reg.requete(execution)["requete"]
        if (len(intentions) != 1 or intentions[0]["requete_sha256"] != empreinte(dossier / "requete.json")
                or spec["execution_id"] != execution or spec["tache"] != row["tache"]
                or spec["numero"] != row["numero"]
                or spec["requete_registre_sha256"] != requete["empreinte_requete"]):
            raise ValueError("Intention et requête du registre non corrélées")
        if not echeance_comparable(spec):
            self.log("echeance_inconnue", execution_id=execution,
                     motif="Démarrage machine différent ou non déclaré ; réservation conservée")
            return False
        # Rattacher dès que la naissance est observée, avant d'attendre la fin.
        observation = self.adaptateur.observe(dossier)
        while observation["correlation"] is None and time.monotonic() < spec["echeance_monotone"]:
            time.sleep(.01)
            observation = self.adaptateur.observe(dossier)
        if observation["correlation"] is None:
            self.log("lancement_inconnu", execution_id=execution)
            return False
        correlation = observation["correlation"]
        identite = correlation["identite"]
        agent = "linux:" + identite["boot"] + ":" + str(identite["pid"]) + ":" + identite["naissance"]
        self.verifier_verrou()
        if row["phase"] == "reservee":
            self.reg.attacher(execution, agent)  # Pas de modèle/effort prétendument appliqué.
            self.point_controle("rattachee")
        elif row["agent"] != agent:
            raise ValueError("Rédacteur du registre différent de la preuve")
        vus = {e.get("execution_id") for e in evenements(self.racine / "controleur.jsonl")
               if e["type"] == "activite_observee"}
        if observation["evenements"] and execution not in vus:
            self.reg.battement(execution)
            self.log("activite_observee", execution_id=execution)
        # Réconciliation même après crash entre spawn et rattachement.
        preuve = self.adaptateur.reconcile(dossier)
        if preuve is None:
            self.log("lancement_inconnu", execution_id=execution)
            return False
        self.point_controle("arretee")
        if preuve["code"] != 0 or preuve["timeout"]:
            self.reg.liberer(execution, json.dumps(preuve, ensure_ascii=False))
            self.point_controle("liberee")
            self.log("echec", execution_id=execution, code=preuve["code"], timeout=preuve["timeout"])
            return True
        try:
            resultat = self.verifier_resultat(execution)
        except (ValueError, OSError, KeyError, TypeError) as erreur:
            self.log("resultat_refuse", execution_id=execution, motif=str(erreur))
            self.reg.liberer(execution, json.dumps(preuve, ensure_ascii=False))
            return True
        self.verifier_verrou()
        canonique = Path(row["fichier"])
        if self.reg.chemin(row["fichier"]) != row["fichier"]:
            raise ValueError("Chemin canonique changé : publication refusée")
        contenu = lire(dossier / "resultat.json")
        if canonique.exists() and canonique.read_bytes() != (dossier / "resultat.json").read_bytes():
            raise ValueError("Sortie canonique différente : publication refusée")
        ecrire(canonique, contenu)
        self.point_controle("publiee")
        # Vérifier aussi après publication, avant soumission puis acceptation.
        resultat = self.verifier_resultat(execution)
        row = self.reg.execution(execution)
        if row["phase"] == "lance":
            self.reg.soumettre(execution, {"C-01": resultat})
            self.point_controle("soumise")
        self.reg.liberer(execution, json.dumps(preuve, ensure_ascii=False))
        self.point_controle("liberee")
        self.accepter(row["tache"], execution)
        return True

    def accepter(self, tache, execution):
        preuve = self.adaptateur.reconcile(self.dossier(execution), attendre=False)
        if preuve is None or preuve["code"] != 0 or preuve["timeout"]:
            raise ValueError("Arrêt réussi non confirmé : acceptation refusée")
        self.verifier_resultat(execution)
        row = self.reg.execution(execution, active=False)
        if empreinte(row["fichier"]) != empreinte(self.dossier(execution) / "resultat.json"):
            raise ValueError("Publication modifiée : acceptation refusée")
        self.reg.accepter(MISSION, tache, "verificateur-deterministe")
        self.point_controle("acceptee")
        self.log("resultat_accepte", execution_id=execution, tache=tache)

    def derniere(self, tache):
        return next(t for t in self.reg.etat(MISSION)["taches"] if t["id"] == tache)["derniere_execution"]

    def reprise_autorisee(self, tache):
        config = self.entrees_valides()
        row = self.reg.tache(MISSION, tache)
        derniere = self.derniere(tache)
        if (tache != "T1" or not config["reprise_autorisee"]
                or row["tentatives"] >= row["maximum"] or not derniere
                or self.reg.manquantes(MISSION, tache)):
            self.log("reprise_refusee", tache=tache, delegation=config["reprise_autorisee"],
                     tentatives=row["tentatives"], maximum=row["maximum"],
                     motif="Délégation, limite ou dépendance incompatible")
            return False
        arret = self.adaptateur.reconcile(self.dossier(derniere["id"]), attendre=False)
        autorisee = arret is not None and arret["code"] == 75 and not arret["timeout"]
        if not autorisee:
            self.log("reprise_refusee", tache=tache, execution_id=derniere["id"],
                     motif="Arrêt inconnu, timeout ou échec hors du code 75 de ce scénario")
        return autorisee

    def resultat(self, motif=None):
        etat = self.reg.etat(MISSION) if self.reg is not None else None
        complet = (etat is not None and not etat["actives"] and len(etat["taches"]) == 2
                   and all(t["etat"] == "terminee" and t["validite"] == "valide" for t in etat["taches"]))
        return {"etat": "succes" if complet and motif is None else "partiel", "motif": motif,
                "registre": etat, "appels_modeles": 0, "type_execution": "processus_logiciel_fixe"}

    def _poursuivre(self, reprendre_suspension):
        self.configuration()
        if lire(self.racine / "controle.json")["suspendue"]:
            if not reprendre_suspension:
                return self.resultat("Mission suspendue ; reprise explicite requise")
            ecrire(self.racine / "controle.json", {"suspendue": False})
            self.log("suspension_levee_explicitement")
        self.entrees_valides()
        # Le registre détermine les états ; les reçus n'en sont pas une copie.
        while True:
            self.entrees_valides()
            actives = self.reg.etat(MISSION)["actives"]
            if actives:
                if len(actives) != 1 or not self.traiter(actives[0]["id"]):
                    return self.resultat("Lancement ou effet inconnu ; réservation conservée")
                continue
            avance = False
            for tache in ("T1", "T2"):
                row = self.reg.tache(MISSION, tache)
                if row["etat"] == "a_verifier":
                    self.accepter(tache, self.derniere(tache)["id"])
                    avance = True
                    break
                if row["etat"] == "bloquee" and self.reprise_autorisee(tache):
                    self.reg.reprendre(MISSION, tache, "Code 75 récupérable du scénario fixe ; arrêt confirmé et délégation valide")
                    self.point_controle("reprise_preparee")
                    self.log("reprise_autorisee", tache=tache)
                    avance = True
                    break
                if (row["etat"] == "a_faire" and not self.reg.manquantes(MISSION, tache)
                        and row["tentatives"] < row["maximum"]):
                    self.preparer(tache)
                    avance = True
                    break
            if not avance:
                resultat = self.resultat()
                if resultat["etat"] != "succes":
                    resultat["motif"] = "Aucune tâche prête : résultat refusé, reprise interdite ou limite atteinte"
                return resultat

    def _finaliser(self, resultat):
        # Le premier SIGINT peut arriver dans ce nettoyage, pas seulement dans
        # la boucle principale. Les suivants ne doivent pas abandonner l'arrêt.
        with _sigint_differe() as interruption:
            incomplets = []
            registre_non_ferme = False
            try:
                for _ in range(2):
                    try:
                        incomplets = self.adaptateur.fermer()
                        break
                    except KeyboardInterrupt:
                        # Cancellation levée directement par un adaptateur, distincte
                        # du signal réel différé ; une seule reprise de nettoyage.
                        interruption["recue"] = True
                    except subprocess.TimeoutExpired:
                        incomplets = list(self.adaptateur.enfants)
                        break
                else:
                    incomplets = list(self.adaptateur.enfants)
            finally:
                if self.reg is not None:
                    for _ in range(2):
                        try:
                            self.reg.fermer()
                            break
                        except KeyboardInterrupt:
                            interruption["recue"] = True
                    else:
                        registre_non_ferme = True
            # Utiliser le dernier état déjà lu : la connexion est maintenant fermée.
            if interruption["recue"]:
                ecrire(self.racine / "controle.json", {"suspendue": True})
                self.log("suspension_utilisateur_pendant_nettoyage")
                if resultat is None:
                    resultat = {"registre": None, "appels_modeles": 0,
                                "type_execution": "processus_logiciel_fixe"}
                resultat.update(etat="partiel", motif="Mission suspendue pendant le nettoyage")
            if resultat is not None and incomplets:
                resultat["etat"] = "partiel"
                motif = "arrêt non confirmé pendant le nettoyage ; réservations conservées"
                resultat["motif"] = ((resultat["motif"] + "; " + motif) if interruption["recue"] else motif)
                resultat["arrets_non_confirmes"] = [Path(p).name for p in incomplets]
            if resultat is not None and registre_non_ferme:
                resultat["fermeture_registre_non_confirmee"] = True
            return resultat

    def run(self, reprendre_suspension=False):
        with verrou(self.racine) as verifier:
            self.verifier_verrou = verifier
            self.reg = None
            resultat = None
            try:
                # L'interruption peut arriver pendant l'ouverture SQLite elle-même.
                self.reg = Superviseur(self.racine / "registre.sqlite")
                resultat = self._poursuivre(reprendre_suspension)
            except KeyboardInterrupt:
                ecrire(self.racine / "controle.json", {"suspendue": True})
                self.log("suspension_utilisateur")
                resultat = self.resultat("Mission suspendue par interruption explicite")
            except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, subprocess.TimeoutExpired) as erreur:
                if self.reg is None:
                    raise  # La CLI distingue encore une base absente ou endommagée.
                resultat = self.resultat(str(erreur))
            finally:
                # os._exit/crash machine échappent à finally : resume réconcilie.
                resultat = self._finaliser(resultat)
            return resultat


def suspendre(destination):
    racine = Path(destination).resolve()
    with verrou(racine):
        ecrire(racine / "controle.json", {"suspendue": True})


def etat(destination):
    racine = Path(destination).resolve()
    with verrou(racine):
        reg = Superviseur(racine / "registre.sqlite")
        try:
            return {"registre": reg.etat(MISSION), "controle": lire(racine / "controle.json"),
                    "appels_modeles": 0}
        finally:
            reg.fermer()
