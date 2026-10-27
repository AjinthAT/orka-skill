"""Reçus durables et identité Linux ; aucune autorité sur les tâches."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid


def lire(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def empreinte(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def synchroniser_dossier(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ecrire(path, valeur):
    """Remplacement atomique, fichier puis dossier synchronisés, sur Linux local."""
    path = Path(path)
    temporaire = path.with_name("." + path.name + "." + uuid.uuid4().hex)
    try:
        with temporaire.open("x", encoding="utf-8") as flux:
            json.dump(valeur, flux, ensure_ascii=False, sort_keys=True)
            flux.write("\n")
            flux.flush()
            os.fsync(flux.fileno())
        os.replace(temporaire, path)
        synchroniser_dossier(path.parent)
    finally:
        temporaire.unlink(missing_ok=True)


def ajouter(path, valeur):
    with Path(path).open("a", encoding="utf-8") as flux:
        flux.write(json.dumps(valeur, ensure_ascii=False, sort_keys=True) + "\n")
        flux.flush()
        os.fsync(flux.fileno())


def evenements(path):
    path = Path(path)
    if not path.exists():
        return []
    contenu = path.read_text(encoding="utf-8")
    if contenu and not contenu.endswith("\n"):
        raise ValueError("Journal tronqué : réconciliation nécessaire")
    return [json.loads(ligne) for ligne in contenu.splitlines()]


def verifier_plateforme():
    if sys.platform != "linux" or not Path("/proc/sys/kernel/random/boot_id").is_file():
        raise ValueError("AUT-02A qualifié uniquement sur Linux avec /proc et flock")


def identite(pid):
    """PID + naissance noyau + démarrage machine ; le PID seul ne suffit pas."""
    verifier_plateforme()
    texte = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    champs = texte[texte.rfind(")") + 2:].split()
    return {"pid": pid, "naissance": champs[19],
            "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}, champs[0]


def observer(identifiant):
    if identifiant["boot"] != Path("/proc/sys/kernel/random/boot_id").read_text().strip():
        return "inconnu"
    try:
        actuelle, etat = identite(identifiant["pid"])
    except FileNotFoundError:
        return "absent"
    except (OSError, ValueError, IndexError):
        return "inconnu"
    if actuelle != identifiant:
        return "remplace"
    return "arrete" if etat in ("Z", "X") else "actif"


@contextmanager
def verrou(racine):
    """Verrou noyau non hérité par les travailleurs ; jamais supprimé au déverrouillage."""
    verifier_plateforme()
    import fcntl
    path = Path(racine) / "controleur.lock"
    with path.open("a+") as flux:
        try:
            fcntl.flock(flux, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Un contrôleur possède déjà cette base") from None

        def verifier():
            a, b = os.fstat(flux.fileno()), path.stat()
            if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
                raise ValueError("Propriétaire du verrou incertain : arrêt des lancements")

        try:
            verifier()
            yield verifier
        finally:
            fcntl.flock(flux, fcntl.LOCK_UN)
