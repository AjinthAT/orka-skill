# Évaluer la simulation Claude avec Inspect AI

Propriétaire : coordinateur de maintenance. Version : 1. Date : 23 octobre 2026.
Provenance : demande de raccorder la simulation Claude à Inspect AI, avec scorers déterministes, sans modèle réel et en préservant L4.

Le [raccordement](../tools/prototype_sdk_inspect/inspect_simulated.py) fournit un solver Inspect personnalisé qui exécute le vrai client Python Claude avec son [transport local simulé](ADAPTATEUR-CLAUDE-SDK.md#transport-simulé-à-chaque-génération). Ses outils MCP utilisent le backend Docker P0/P1 inchangé. Deux scorers déterministes examinent le livrable physique et les preuves d’exécution. Il n’utilise pas `agent_bridge` : ce parcours ne doit router aucun appel modèle ni ouvrir de proxy HTTP.

## Installer l’environnement séparé

Le [verrou propre à ce parcours](../tools/prototype_sdk_inspect/requirements-inspect-claude.lock) fixe `inspect-ai==0.3.283`, `claude-agent-sdk==0.2.173`, `mcp==2.3.0` et les empreintes de leurs dépendances. Sa [provenance](../tools/prototype_sdk_inspect/inspect-dependency-lock.json) lie verrou, contrat P0/P1 et scénarios. Les verrous précédents restent inchangés. La résolution universelle vise Python 3.12 ; le contrôleur effectivement essayé est macOS ARM64 et le worker Linux ARM64. Les autres environnements ne sont pas qualifiés par cette réception.

Depuis la racine du dépôt :

```sh
uv venv --python python3.12 .orka/venvs/claude-inspect
uv pip sync --python .orka/venvs/claude-inspect/bin/python --require-hashes tools/prototype_sdk_inspect/requirements-inspect-claude.lock
```

Cette préparation peut télécharger des paquets ; l’évaluation suivante n’en télécharge aucun. L’image Docker P0/P1 doit déjà être en cache, selon le [guide du backend](PROTOTYPE-SDK-INSPECT.md). Aucun compte, clé API ou modèle n’est requis.

## Exécuter l’évaluation logicielle

Dans son propre processus Python, avec un nouveau nom de destination dont le parent existe :

```sh
.orka/venvs/claude-inspect/bin/python -B -m tools.prototype_sdk_inspect.inspect_simulated --destination .orka/prototype-sdk-inspect/inspect-claude-essai-01
```

Le programme refuse une destination existante, fixe un seul échantillon et une seule tâche à la fois, un epoch et zéro relance sur erreur. Chaque échantillon reçoit un workspace P0/P1 et un identifiant de worker distincts ; une session ne peut pas être réutilisée pour remettre ses compteurs à zéro.

Inspect est fixé à `mockllm/model` comme identifiant technique, mais sa méthode `Model.generate` est interdite pendant l’évaluation. Le solver n’appelle jamais le paramètre `generate` fourni par Inspect. Les réponses Claude sont les éléments d’un script local figé, consommés par le transport déjà qualifié. Même le générateur du fournisseur factice Inspect n’est pas appelé. Le reçu final exige zéro tentative de génération et un registre de consommation modèle vide.

Des gardes temporaires empêchent les connexions réseau Python, les transports Claude par défaut et les sous-processus autres que les commandes Docker du backend. Elles s’appliquent au processus entier : ne pas importer ce runner dans un service qui effectue d’autres travaux simultanés. Aucun réglage personnel n’est modifié. Le journal Inspect reste local, ses contrôleurs ACP/CTL et notifications sont désactivés. La collecte facultative de révision Git par Inspect est désactivée pour conserver cette restriction des processus ; `provenance.json` enregistre les empreintes exactes des sources utilisées.

## Scénarios et notation

Les [11 scripts figés](../tools/prototype_sdk_inspect/inspect-scenarios.json) utilisent uniquement les quatre cas fictifs P0/P1. Leurs réponses ont été écrites explicitement pour vérifier le logiciel. Les valeurs attendues des cas restent dans le contrôleur et les cibles Inspect ; elles ne sont pas envoyées au client Claude. Les scripts contiennent volontairement des réponses connues, correctes ou incorrectes : ces résultats ne mesurent pas la capacité d’un modèle à trouver une réponse.

| Scénarios | `livrable` attendu | `execution` attendue |
|---|---:|---:|
| `complet_ok`, `manquant_ok`, `contradiction_ok`, `hostile_ok` | 1 | 1 |
| Total faux, prix inventé, ancienne version, fausse preuve terrain | 0 | 1 |
| Réponse finale correcte sans écriture de fichier | 0 | 1 |
| JSON écrit avec clé dupliquée | 0 | 1 |
| Arrêt du script après une écriture correcte | 1 | 0 |

Le [scorer `livrable`](../tools/prototype_sdk_inspect/inspect_scoring.py) lit la copie des octets du fichier effectivement observé après arrêt. Il exige une écriture réussie unique, dont les arguments, la réponse SDK, le journal worker, la taille et le SHA-256 concordent. Il ne note jamais `state.output` ni une affirmation de l’assistant. Pour ces fixtures, le JSON attendu doit correspondre exactement aux champs et types figés ; clés dupliquées, valeurs non finies, champ inventé et confusion entre `false`, `null` et `0` sont refusés. Ce contrat de test ne modifie pas les règles métier du skill.

Le scorer `execution` exige une fin normale du script, un catalogue conforme à chaque génération, la corrélation des appels SDK avec les événements worker et leur séquence, les empreintes d’entrées préservées, des sorties correspondant aux créations constatées et un reçu de fin confirmant l’arrêt du worker. Un refus de lecture hors inventaire est attendu dans les deux scénarios hostiles ; il valide le contrôle d’accès lorsque le script se termine normalement. Un refus inattendu ou un arrêt de transport ne valide pas l’exécution.

Les deux scores sont séparés : le fichier d’une exécution interrompue peut être correct tout en restant non accepté comme résultat de mission. Le programme compare les scores réels à la matrice de contrôle figée et retourne le code 2 en cas d’écart ou d’erreur. Un succès de cette réception logicielle signifie que les contrôles positifs et négatifs réagissent correctement. Les moyennes affichées par Inspect mélangent volontairement ces cas ; elles ne constituent pas une performance d’Orka ou d’un modèle.

## Traces et reprise

```text
destination/
  provenance.json                 empreintes du raccordement et des dépendances
  reception.json                  scores réels/attendus et compteurs sans modèle
  logs/*.json                     journal Inspect, scores et store par échantillon
  runs/<scenario>/
    inputs/                       copies autorisées en lecture seule
    outputs/                      remises, y compris sorties incorrectes/interrompues
    runtime/                      backend figé
    controle/                     manifestes, reçus, événements et observation Inspect
```

`controle/inspect-observation.json` conserve les enveloppes simulées acceptées et leurs empreintes, les opérations SDK corrélées, le résultat terminal, le fichier observé, les empreintes d’entrées et les preuves d’arrêt/isolation. Le store privé du sample Inspect en contient une copie. La grille et les traces ne sont pas ajoutées au catalogue des trois outils. Le champ de préparation `sdk_inspect` des manifestes P0/P1 conserve son état initial ; le résultat de l’étape Inspect est dans les observations et le reçu racine.

Une erreur du framework peut laisser une réception partielle, des logs et des fichiers déjà créés ; les conserver et utiliser une nouvelle destination pour un nouvel essai. Ne pas supprimer un reçu de démarrage pour forcer la reprise d’un worker. Les captures sous `.orka/` sont privées et ignorées par Git ; leur conservation locale n’est pas une sauvegarde. Le rapport de [réception observée](VALIDATION-INSPECT-CLAUDE-SIMULE.md) identifie les preuves de cette livraison.

## Vérifier sans modèle

```sh
ORKA_INSPECT_SIMULATION=1 ORKA_P01_DOCKER=1 .orka/venvs/claude-inspect/bin/python -B -m unittest discover -s tests -p test_inspect_simulated.py -v
ORKA_CLAUDE_SDK=1 ORKA_P01_DOCKER=1 .orka/venvs/claude-inspect/bin/python -B -m unittest discover -s tests -p 'test_claude*.py' -v
```

Les dix contrôles portables des scorers sont inclus dans le vérificateur du dépôt, sans installer Inspect. Les contrôles du vrai framework et la matrice Docker sont activés explicitement. Les tests unitaires fabriquent leurs preuves de notation et les identifient comme telles ; le test d’intégration utilise les vrais fichiers, scripts, reçus Docker et logs Inspect.

Le backend, les cas P0/P1, le transport Claude et L4 restent inchangés. Ce raccordement qualifie le segment Claude–Inspect simulé ; le parcours OpenAI Agents SDK du plan, un transport vers un fournisseur réel, le CLI Claude Code et un comportement de modèle restent à qualifier.

Sources consultées le 23 octobre 2026 via Context7 et confrontées au paquet installé : [solvers Inspect](https://inspect.aisi.org.uk/solvers.html), [scorers](https://inspect.aisi.org.uk/scorers.html), [API de l’évaluation](https://inspect.aisi.org.uk/reference/inspect_ai.html).
