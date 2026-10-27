"""Programme fixe de recette. Pas de commande arbitraire, réseau, SDK ou descendant."""

import csv
import json
import os
from pathlib import Path
import sys
import time

# Exécuté en chemin absolu avec Python isolé (-I), sans PYTHONPATH utilisateur.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stockage import ajouter, ecrire, empreinte, identite, lire


def executer(dossier):
    dossier = Path(dossier)
    spec = lire(dossier / "requete.json")
    correlation = {"execution_id": spec["execution_id"],
                   "requete_sha256": empreinte(dossier / "requete.json"),
                   "identite": identite(os.getpid())[0]}
    ecrire(dossier / "demarre.json", correlation)
    incident = spec["incident"] if spec["tache"] == "T1" else "aucun"
    if incident != "silence":
        ajouter(dossier / "evenements.jsonl", dict(correlation, type="debut_logiciel"))
    if incident == "silence":
        time.sleep(60)
    if incident == "retour-tardif":
        time.sleep(1)
    code = 0
    if incident == "erreur-permanente":
        code = 65
    elif incident == "epuisement" or (incident == "aucun" and spec["tache"] == "T1" and spec["numero"] == 1):
        code = 75
    elif incident != "sortie-absente":
        if spec["tache"] == "T1":
            with (dossier / "entree.csv").open(encoding="utf-8", newline="") as flux:
                total = sum(int(ligne["montant"]) for ligne in csv.DictReader(flux))
            if incident == "mauvais-total":
                total += 1
            if incident == "mauvais-type":
                total = str(total)
            resultat = {"total_net": total}
        else:
            total = lire(dossier / "amont.json")["total_net"]
            resultat = {"total_net": total, "source_sha256": empreinte(dossier / "amont.json"),
                        "bilan": f"Total net vérifié : {total}."}
        ecrire(dossier / "resultat.json", resultat)
    ecrire(dossier / "termine.json", dict(correlation, code=code, fin_monotone=time.monotonic()))
    return code


if __name__ == "__main__":
    sys.exit(executer(sys.argv[1]))
