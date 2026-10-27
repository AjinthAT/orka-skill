import os,signal,sys,time
from pathlib import Path
from tools.supervision_locale import __main__ as cli
from tools.supervision_locale.controleur import Controleur
from tools.supervision_locale.stockage import ecrire,identite
racine=Path(sys.argv[1]); c=None
def point(p):
    if p=='lancee':
        dossier=next(iter(c.adaptateur.enfants))
        fin=time.monotonic()+3
        while not (Path(dossier)/'demarre.json').exists():
            assert time.monotonic()<fin
            time.sleep(.01)
        enfant=next(iter(c.adaptateur.enfants.values()))
        os.kill(enfant.pid,signal.SIGSTOP)
        ecrire(racine/'sonde-nettoyage.json',identite(enfant.pid)[0])
        raise ValueError('Incident logiciel injecté après lancement')
def construire(destination):
    global c
    c=Controleur(destination,point)
    return c
cli.Controleur=construire
sys.argv=['supervision_locale','resume','--destination',str(racine)]
sys.exit(cli.main())
