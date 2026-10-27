# Réception AUT-02A

Propriétaire : coordinateur de maintenance. Version documentaire : 1, 27 octobre 2026. Périmètre : [lot AUT-02](LOT-AUT-02.md), étape A uniquement. État : implémenté et vérifié dans le périmètre logiciel Linux ci-dessous. Base : AUT-01 `a9d4a11` ; empreintes exactes du code dans les nouvelles captures.

## Résultat et périmètre

Le superviseur facultatif est dans [tools/supervision_locale](../tools/supervision_locale/controleur.py), hors paquet du skill. Le registre v2 existant reste l'autorité ; aucune table ni commande de son API n'est modifiée. Les travailleurs sont des programmes Python fixes, sans fournisseur, réseau ni modèle. Le [guide](SUPERVISEUR-LOCAL.md) fournit les commandes de démonstration, état, suspension et reprise.

La recette nominale exécute T1 deux fois (code 75 puis résultat correct), accepte le total net 115 recalculé, puis exécute et accepte T2 dépendante. Chaque tentative conserve sa requête, ses entrées, l'identité réelle du processus, ses sorties et son arrêt observé. Aucun profil demandé dans le registre n'est déclaré appliqué à un modèle.

Les [captures nouvelles](../evals/supervision-AUT-02A-2026-10-27/README.md) conservent trois parcours : nominal réussi, mauvais total refusé malgré code 0 et crash réel après publication suivi d'une reprise réussie sans quatrième travailleur. Les empreintes des fichiers bruts figurent dans leur manifeste. Ces captures ont été produites après la suite globale, avec le même code source.

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

Vérification finale exécutée : `python -B tools/verifier.py`, code de sortie 0, **166 tests recensés : 125 réussis et 41 optionnels ignorés**, dont les **35 nouveaux tests AUT-02A réussis**. Le vérificateur confirme les liens maintenus, l'installation déplacée des outils historiques, le contenu exact du ZIP et sa version 0.9.0. `git diff --check` est également propre. Aucun test optionnel SDK/Docker/modèle n'a été activé.

## Limites de la réception

Qualification initiale sur Linux x86_64/Python 3.14.3 avec `/proc`, `flock` et `pidfd` exposés. La cible syntaxique reste Python 3.10+ ; l'exécution des autres versions et systèmes n'est pas démontrée par cette réception. Les tests de processus sont ignorés explicitement hors Linux.

Un lancement sans preuve suffisante, un journal tronqué ou un changement de code/mandat garde un état partiel. Aucun outil de forçage ou de remise à zéro n'est fourni. Les programmes fixes n'ont pas de descendants ; ce résultat ne qualifie ni des commandes arbitraires, ni le CLI Codex, ni un sandbox. Aucun service permanent, agent modèle, juge IA ou gain comparatif de qualité n'est revendiqué.

La documentation Python a été consultée via Context7 (`/python/cpython`) pour les [délais de `Popen.wait`](https://github.com/python/cpython/blob/main/Doc/library/subprocess.rst) et [verrous `flock`](https://github.com/python/cpython/blob/main/Doc/library/fcntl.rst). Un délai expiré ne termine pas un processus ; l'implémentation exige un constat distinct avant libération.
