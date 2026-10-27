# Réception AUT-02A

Propriétaire : coordinateur de maintenance. Version documentaire : 3, 27 octobre 2026. Périmètre : [lot AUT-02](LOT-AUT-02.md), étape A uniquement, puis corrections de ses revues. Base : AUT-01 `a9d4a11` ; première réception sur `ce644e6`, premières corrections sur `697d5a0`. Les preuves précédentes sont conservées ; chaque réception est distinguée ci-dessous.

## Résultat et périmètre

Le superviseur facultatif est dans [tools/supervision_locale](../tools/supervision_locale/controleur.py), hors paquet du skill. Le registre v2 existant reste l'autorité ; aucune table ni commande de son API n'est modifiée. Les travailleurs sont des programmes Python fixes, sans fournisseur, réseau ni modèle. Le [guide](SUPERVISEUR-LOCAL.md) fournit les commandes de démonstration, état, suspension et reprise.

La recette nominale exécute T1 deux fois (code 75 puis résultat correct), accepte le total net 115 recalculé, puis exécute et accepte T2 dépendante. Chaque tentative conserve sa requête, ses entrées, l'identité réelle du processus, ses sorties et son arrêt observé. Aucun profil demandé dans le registre n'est déclaré appliqué à un modèle.

Les [captures initiales](../evals/supervision-AUT-02A-2026-10-27/README.md) conservent trois parcours : nominal réussi, mauvais total refusé malgré code 0 et crash réel après publication suivi d'une reprise réussie sans quatrième travailleur. Les empreintes des fichiers bruts figurent dans leur manifeste. Elles décrivent la révision initiale `ce644e6`, avant les corrections de revue, et restent inchangées.

## Contrôles

La [suite AUT-02A](../tests/test_supervision_locale.py) utilise des dossiers temporaires et de vrais sous-processus. Elle comprend les fenêtres de crash avant/après lancement, rattachement, arrêt, publication, soumission, libération et acceptation ; la création incertaine garde sa réservation. Après crash, un travailleur identifiable encore actif est attendu, jamais remplacé. Une fin logicielle n'est admise qu'avec un arrêt observé de la même naissance Linux ; les arrêts après perte du parent utilisent `pidfd` quand disponible.

| Critère du lot | Preuve et portée AUT-02A |
|---|---|
| A01 | Sources du cœur inchangées ; installateur et tests de contenu du ZIP ; superviseur hors `.agents/skills/orka/` |
| A02 | Test de réservation dans le registre avant chaque `Popen`, trois identités réelles ; exclusion entre deux contrôleurs par `flock` |
| A03–A04 | Premier échec sans artefact et sans soumission ; arrêt conservé ; motif de reprise ; compteurs T1=2/T2=1 et trois travailleurs |
| A05 | Refus sans délégation, limite 1/2, erreur permanente, source modifiée, effet inconnu ; adoption de l'ancien rédacteur actif |
| A06 | Recalcul 115 ; refus d'artefact absent malgré code 0, mauvaise valeur et mauvais type ; sorties incorrectes conservées dans la tentative |
| A07 | Mutation amont après acceptation et après réservation aval ; publication modifiée après soumission ; aucune acceptation aval périmée |
| A08 | Crashs réels par `os._exit`, nouvelle instance du contrôleur sur la même base ; trois travailleurs au total lorsque la réconciliation est prouvée, réservation conservée sinon |
| A09 | Silence, timeout, résultat tardif après crash, identité inconnue et PID remplacé ; aucun signal global ni publication tardive acceptée |
| A10 | Compteurs persistants, destination existante refusée, suspension par API et `SIGINT` réel ; reprise explicite nécessaire |
| A11 | Succès uniquement avec T1/T2 acceptées et valides, aucune réservation active ; état partiel avec motif sinon |
| A12 | Hors AUT-02A : aucun adaptateur Codex ni essai de flux fournisseur |
| A13 | `appels_modeles=0`, type logiciel explicite, paramètres appliqués inconnus ; pas de lecture de configuration/authentification fournisseur |
| A14 | Suite globale, paquet et liens valides ; aucune modification du cœur distribué, des captures historiques, du prototype ou de L4 ; pas de migration de schéma |

Première vérification, avant revue : `python -B tools/verifier.py`, code de sortie 0, **166 tests recensés : 125 réussis et 41 optionnels ignorés**, dont les **35 tests AUT-02A réussis**. Le vérificateur confirmait les liens maintenus, l'installation déplacée des outils historiques, le contenu exact du ZIP et sa version 0.9.0. Ces résultats n'avaient pas couvert les trois défauts de revue ci-dessous.

## Corrections de revue

1. **Échéance et démarrage machine.** La requête fige le démarrage avec son échéance monotone. Le contrôleur et l'adaptateur refusent immédiatement une échéance d'un autre démarrage ou sans provenance, sans attendre, signaler un PID ou relancer le travailleur. La réservation reste active.
2. **Interruption pendant l'ouverture SQLite.** Le gestionnaire `KeyboardInterrupt` couvre l'ouverture du registre sous le verrou du contrôleur. La suspension est persistée, même sans objet registre disponible ; une reprise normale ne la lève pas.
3. **Arrêt non confirmé.** L'expiration de la dernière attente après `kill` retourne un constat inconnu. Le nettoyage borné collecte les arrêts non confirmés ; le JSON final est partiel et conserve les réservations, sans preuve d'arrêt inventée ni exception de délai non gérée. Un résultat de tâches complet ne masque pas un nettoyage incomplet.

Sept tests de régression complètent les 35 tests initiaux : changement de démarrage dans le contrôleur et l'adaptateur, démarrage absent, `SIGINT` réel pendant une ouverture SQLite verrouillée, interruption sans objet registre, absence de confirmation après `kill`, nettoyage sans reçu et interdiction d'un succès après nettoyage incomplet. Les variantes regroupées dans un même test restent distinctes dans les assertions. Les délais non confirmés et le redémarrage machine sont simulés ; aucun redémarrage de l'hôte n'est effectué.

La [première réception corrective](../evals/corrections-AUT-02A-2026-10-27/README.md), sur `697d5a0`, conserve ses résultats sans réécrire les anciennes captures : **173 tests recensés, 132 réussis et 41 optionnels ignorés**, dont les **42 tests AUT-02A réussis** (35 initiaux et sept régressions). Les sept régressions échouent chacune sur une copie temporaire de `ce644e6` ; les journaux avant/après sont conservés. Le paquet portable 0.9.0, les liens maintenus et les empreintes des captures étaient vérifiés ; un parcours nominal réussissait avec trois travailleurs, sans appel modèle.

## SIGINT pendant le nettoyage

La relecture de `697d5a0` a trouvé un chemin supplémentaire : un premier `SIGINT` pouvait interrompre le bloc `finally`, après la sortie de la boucle principale. La finalisation mémorise maintenant ce signal sans lever d'exception depuis son gestionnaire, poursuit les arrêts bornés et ferme le registre. Elle persiste ensuite la suspension et rend un JSON partiel à partir du dernier état déjà lu. Le gestionnaire de signal précédent est rétabli à la sortie de cette phase ; aucune écriture ne se fait dans le gestionnaire du signal.

Trois régressions couvrent un SIGINT réel pendant le nettoyage d'un travailleur mis en pause, un SIGINT pendant la fermeture du registre, et des signaux répétés avec arrêt simulé non confirmé. Dans ce dernier cas, les attentes ne recommencent pas, la réservation reste active et aucun reçu d'arrêt n'est fabriqué. La reprise sans levée explicite respecte la suspension.

La [nouvelle réception](../evals/sigint-nettoyage-AUT-02A-2026-10-27/README.md) conserve les trois échecs sur la référence et les résultats corrigés. **Validation globale finale : 176 tests recensés, 135 réussis et 41 optionnels ignorés**, dont les **45 tests AUT-02A réussis**. Le paquet portable reste en 0.9.0 ; le cœur et toutes les captures précédentes sont inchangés. La sonde réelle rend un JSON partiel, conserve la suspension et observe le travailleur arrêté. Aucun modèle, noyau volontairement bloqué ou redémarrage de machine n'est impliqué.

## Limites de la réception

Qualification initiale sur Linux x86_64/Python 3.14.3 avec `/proc`, `flock` et `pidfd` exposés. La cible syntaxique reste Python 3.10+ ; l'exécution des autres versions et systèmes n'est pas démontrée par cette réception. Les tests de processus sont ignorés explicitement hors Linux.

Un lancement sans preuve suffisante, un journal tronqué ou un changement de code/mandat garde un état partiel. Aucun outil de forçage ou de remise à zéro n'est fourni. Les programmes fixes n'ont pas de descendants ; ce résultat ne qualifie ni des commandes arbitraires, ni le CLI Codex, ni un sandbox. Aucun service permanent, agent modèle, juge IA ou gain comparatif de qualité n'est revendiqué.

La documentation Python a été consultée via Context7 (`/python/cpython`) pour les [délais de `Popen.wait`](https://github.com/python/cpython/blob/main/Doc/library/subprocess.rst) et [verrous `flock`](https://github.com/python/cpython/blob/main/Doc/library/fcntl.rst). Un délai expiré ne termine pas un processus ; l'implémentation exige un constat distinct avant libération.

La [gestion Python des signaux](https://github.com/python/cpython/blob/main/Doc/library/signal.rst) a également été consultée pour la mémorisation de SIGINT pendant une section critique et la restauration du gestionnaire précédent dans le thread principal.
