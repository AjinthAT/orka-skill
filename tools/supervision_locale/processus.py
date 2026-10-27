"""Adaptateur Linux limité au travailleur logiciel livré avec AUT-02A."""

import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from .stockage import ecrire, empreinte, evenements, lire, observer


TRAVAILLEUR = Path(__file__).with_name("travailleur.py")


class ProcessusFixes:
    def __init__(self):
        self.enfants = {}

    def launch(self, dossier):
        dossier = Path(dossier)
        # Aucun shell, pipe bloquant, outil fournisseur ou commande configurable.
        with (dossier / "stdout.log").open("xb") as sortie, (dossier / "stderr.log").open("xb") as erreur:
            enfant = subprocess.Popen(
                [sys.executable, "-I", "-B", str(TRAVAILLEUR), str(dossier)],
                cwd=dossier, stdin=subprocess.DEVNULL, stdout=sortie, stderr=erreur,
                close_fds=True, start_new_session=True,
                env={"PATH": os.defpath, "LANG": "C.UTF-8"})
        self.enfants[str(dossier)] = enfant
        return enfant.pid

    def correlation(self, dossier):
        dossier = Path(dossier)
        if not (dossier / "demarre.json").exists():
            return None
        debut = lire(dossier / "demarre.json")
        spec = lire(dossier / "requete.json")
        if (set(debut) != {"execution_id", "requete_sha256", "identite"}
                or debut["execution_id"] != spec["execution_id"]
                or debut["requete_sha256"] != empreinte(dossier / "requete.json")):
            raise ValueError("Reçu de lancement incompatible")
        enfant = self.enfants.get(str(dossier))
        if enfant is not None and enfant.pid != debut["identite"]["pid"]:
            raise ValueError("PID du reçu différent du processus créé")
        return debut

    def observe(self, dossier):
        debut = self.correlation(dossier)
        if debut is None:
            return {"etat": "inconnu", "correlation": None, "evenements": []}
        activites = evenements(Path(dossier) / "evenements.jsonl")
        for evenement in activites:
            if any(evenement.get(k) != v for k, v in debut.items()):
                raise ValueError("Événement non corrélé")
        return {"etat": observer(debut["identite"]), "correlation": debut, "evenements": activites}

    def _consigner_arret(self, dossier, debut, code, source, timeout=False):
        preuve = dict(debut, code=code, preuve=source, timeout=timeout,
                      type_execution="processus_logiciel_fixe", appels_modeles=0)
        ecrire(Path(dossier) / "arret.json", preuve)
        return preuve

    def _fin(self, dossier, debut):
        termine = lire(Path(dossier) / "termine.json")
        if (any(termine.get(k) != v for k, v in debut.items())
                or type(termine.get("code")) is not int
                or type(termine.get("fin_monotone")) not in (int, float)
                or not math.isfinite(termine["fin_monotone"])):
            raise ValueError("Reçu de fin incompatible")
        return termine

    def stop(self, dossier):
        """Un délai seul ne donne jamais un reçu d'arrêt."""
        dossier = Path(dossier)
        debut = self.correlation(dossier)
        if debut is None:
            return None
        enfant = self.enfants.get(str(dossier))
        if enfant is not None:
            # Tant qu'un enfant n'est pas récolté, son PID ne peut pas être réutilisé.
            if enfant.poll() is None:
                enfant.terminate()
                try:
                    enfant.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    enfant.kill()
                    enfant.wait(timeout=1)
            return self._consigner_arret(dossier, debut, enfant.returncode, "waitpid contrôleur", True)
        if observer(debut["identite"]) != "actif":
            return self.reconcile(dossier, attendre=False)
        # pidfd ferme la course entre vérification de naissance et signal après reprise.
        if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
            return None
        try:
            fd = os.pidfd_open(debut["identite"]["pid"])
        except ProcessLookupError:
            return self.reconcile(dossier, attendre=False)
        try:
            if observer(debut["identite"]) != "actif":
                return self.reconcile(dossier, attendre=False)
            signal.pidfd_send_signal(fd, signal.SIGKILL)
            fin = time.monotonic() + 1
            while observer(debut["identite"]) == "actif" and time.monotonic() < fin:
                time.sleep(.01)
            if observer(debut["identite"]) not in ("absent", "remplace", "arrete"):
                return None
            return self._consigner_arret(dossier, debut, -signal.SIGKILL,
                                        "pidfd signalé puis naissance arrêtée observée", True)
        finally:
            os.close(fd)

    def reconcile(self, dossier, attendre=True):
        dossier = Path(dossier)
        spec = lire(dossier / "requete.json")
        while True:
            debut = self.correlation(dossier)
            enfant = self.enfants.get(str(dossier))
            if debut is not None:
                etat = observer(debut["identite"])
                if (dossier / "arret.json").exists():
                    preuve = lire(dossier / "arret.json")
                    if any(preuve.get(k) != v for k, v in debut.items()):
                        raise ValueError("Preuve d'arrêt non corrélée")
                    if etat in ("absent", "remplace", "arrete"):
                        if enfant is not None:
                            enfant.wait(timeout=1)
                        return preuve
                    return None
                if enfant is not None and enfant.poll() is not None:
                    retard = time.monotonic() > spec["echeance_monotone"]
                    if (dossier / "termine.json").exists():
                        termine = self._fin(dossier, debut)
                        if termine["code"] != enfant.returncode:
                            raise ValueError("Sortie processus différente du reçu logiciel")
                        retard = termine["fin_monotone"] > spec["echeance_monotone"]
                    return self._consigner_arret(dossier, debut, enfant.returncode, "waitpid contrôleur", retard)
                if etat in ("absent", "remplace", "arrete"):
                    # Sans waitpid, seule la combinaison reçu fini + naissance arrêtée
                    # est admise pour ces programmes fixes sans descendants.
                    if not (dossier / "termine.json").exists():
                        return None
                    termine = self._fin(dossier, debut)
                    return self._consigner_arret(dossier, debut, termine["code"],
                                                "reçu logiciel fini et naissance arrêtée observée",
                                                termine["fin_monotone"] > spec["echeance_monotone"])
                if etat == "inconnu":
                    return None
            if not attendre:
                return None
            if time.monotonic() >= spec["echeance_monotone"]:
                return self.stop(dossier) if debut is not None else None
            time.sleep(.01)

    def fermer(self):
        for dossier, enfant in self.enfants.items():
            if enfant.poll() is None:
                # Attendre brièvement le reçu de naissance avant un arrêt ciblé.
                fin = time.monotonic() + 1
                while not (Path(dossier) / "demarre.json").exists() and time.monotonic() < fin:
                    time.sleep(.01)
                if (Path(dossier) / "demarre.json").exists():
                    try:
                        self.stop(dossier)
                    except (ValueError, OSError, KeyError, TypeError):
                        # Reçu illisible : on peut encore récolter notre propre enfant,
                        # sans inventer de preuve corrélée ni libérer sa réservation.
                        if enfant.poll() is None:
                            enfant.kill()
                        enfant.wait(timeout=1)
                else:
                    # Enfant direct de confiance, encore possédé : waitpid est sûr.
                    enfant.kill()
                    enfant.wait(timeout=1)
            else:
                enfant.wait(timeout=1)
