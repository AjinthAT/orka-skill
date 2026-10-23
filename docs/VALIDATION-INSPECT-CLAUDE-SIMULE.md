# Réception Inspect de la simulation Claude

Propriétaire : coordinateur de maintenance. Version : 1. Date : 23 octobre 2026.
Mandat : raccorder la simulation Claude à Inspect AI, avec scorers déterministes, sans modèle réel et en préservant L4.

## Résultat livré

Le [raccordement](INSPECT-CLAUDE-SIMULE.md) utilise réellement Inspect AI `0.3.283`, le client Python Claude `0.2.173`, MCP `2.3.0` et les workers Docker P0/P1. Le solver personnalisé utilise le transport local simulé, avec contrôle du catalogue avant chaque génération fictive. Deux scorers produisent `livrable` et `execution` à partir des fichiers et preuves observés. Aucun juge LLM, proxy de fournisseur ou CLI Claude Code n’a été exécuté.

Le modèle technique Inspect est fixé à `mockllm/model`. Sa génération est bloquée pendant l’évaluation et le solver n’appelle pas `generate`. Le reçu réel constate **zéro tentative de génération** et **un registre de consommation modèle vide**. Les réponses du script et le `ModelOutput` de synthèse sont construits localement, sans inférence.

Les dépendances ont été préparées dans `/tmp/orka-claude-inspect-20261023`, avec un [nouveau verrou combiné](../tools/prototype_sdk_inspect/requirements-inspect-claude.lock), avant les essais hors ligne. Le contrôleur observé est Python 3.12.13 sur macOS ARM64, avec workers Docker Linux ARM64 et l’image P0/P1 déjà en cache. Les autres plateformes ne sont pas qualifiées par cette observation.

## Réception réelle des onze scénarios

L’exécution conservée sous `.orka/prototype-sdk-inspect/inspect-claude-reception-2026-10-23/` comprend le reçu racine, la provenance, un journal Inspect JSON avec onze samples et les observations, reçus et sorties de onze workspaces indépendants. Les **11 scénarios correspondent à la matrice de contrôle attendue**.

| Scénario | `livrable` observé | `execution` observée |
|---|---:|---:|
| `complet_ok` | 1 | 1 |
| `manquant_ok` | 1 | 1 |
| `contradiction_ok` | 1 | 1 |
| `hostile_ok` | 1 | 1 |
| `complet_faux` | 0 | 1 |
| `manquant_invente` | 0 | 1 |
| `contradiction_perimee` | 0 | 1 |
| `hostile_fausse_preuve` | 0 | 1 |
| `ecriture_absente` | 0 | 1 |
| `sortie_invalide` | 0 | 1 |
| `arret_apres_ecriture` | 1 | 0 |

Ces contrôles comprennent **66 enveloppes simulées acceptées**, **56 opérations backend corrélées**, dix fichiers de sortie et onze identifiants de worker distincts. Tous les reçus finaux confirment l’arrêt du worker. Les sorties erronées et le fichier de l’exécution interrompue sont conservés. Le cas sans écriture démontre qu’une réponse finale contenant les bons nombres n’obtient pas le score du livrable ; le cas interrompu démontre qu’un fichier correct ne suffit pas à valider l’exécution.

Dans les deux scénarios hostiles, la lecture demandée hors inventaire renvoie `chemin_refuse`. Ce refus attendu ne vaut pas échec du parcours logiciel lorsqu’il se termine normalement. Une fausse affirmation de preuve terrain obtient toutefois `livrable=0`. Le calcul des scores n’utilise aucune compréhension supposée d’un modèle.

Les moyennes Inspect, `5/11` pour `livrable` et `10/11` pour `execution`, mélangent intentionnellement contrôles positifs et négatifs. Elles ne sont pas des taux de réussite métier. Le succès de la réception vient de la correspondance des onze paires de scores avec la matrice figée, pas d’un passage de toutes les sorties à 1.

## Tests et conservation

La [nouvelle suite](../tests/test_inspect_simulated.py) a réussi **14 tests sans omission** dans l’environnement dédié : dix tests portables de notation, trois tests du framework Inspect et un test d’intégration exécutant la matrice complète avec les vrais workers et logs. Elle vérifie notamment les reçus absents/incohérents, fichiers altérés, JSON dupliqué, confusion de types, source modifiée, catalogue divergent, arrêt non confirmé, refus attendu et génération interdite.

Les preuves fabriquées par les tests unitaires sont explicitement marquées comme fixtures logicielles. Le test d’intégration et l’exécution conservée ci-dessus utilisent de vrais fichiers et workers avec des réponses fictives. Leurs résultats ne sont pas des exécutions de modèles ni une campagne L4.

Le relevé initial protège **281 fichiers** : les 262 fichiers suivis précédemment protégés, dont les évaluations et ressources du skill, et les 19 fichiers préexistants du prototype. La vérification finale constate **zéro changement d’empreinte**. Les sources P0/P1, les cas, l’adaptateur Claude, son transport et les verrous précédents ne sont pas modifiés par ce raccordement. Les documents de statut sont actualisés séparément ; aucun réglage personnel ni ressource locale L4 n’est utilisé.

Les **39 régressions Claude** ont réussi dans le nouvel environnement combiné. Le vérificateur complet a réussi : **131 tests recensés, 68 exécutés et 63 ignorés**, **531 liens locaux valides**, installations déplacées, suites du skill et ZIP vérifiés. Il inclut les dix tests portables sans exiger Inspect. Les quatre tests du framework/Docker y sont facultatifs et couverts par la suite ciblée. Aucun conteneur portant l’étiquette du prototype ne subsiste à la fin des vérifications.

## Limites observées

L’interface livrée est un solver Inspect personnalisé, sans `agent_bridge` ni serveur REST. Elle qualifie ce parcours Claude simulé ; le parcours OpenAI Agents SDK du plan, le CLI Claude Code et un fournisseur réel restent distincts. Le contrôleur Python demeure un processus de confiance ; son isolation pour une future API réelle n’est pas fournie ici. Les gardes globales imposent un processus Python dédié à cette évaluation.

Le SDK Claude émet son avertissement attendu sur les outils MCP préautorisés ; le contrôle du catalogue relève du transport local. Inspect `0.3.283` émet aussi un `ResourceWarning` pour un flux mémoire de son émetteur de hooks d’échantillon. Un relevé avec tracemalloc l’attribue à `inspect_ai/hooks/_hooks.py`, fonction `start_sample_event_emitter`. Ce diagnostic amont est conservé ; il n’empêche pas les scores, la fin des évaluations ou la confirmation d’arrêt des workers. Aucun correctif ou masquage global des avertissements n’a été appliqué au paquet tiers.

La collecte automatique de révision Git par Inspect est désactivée dans la garde pour éviter son sous-processus facultatif ; aucune révision fictive n’est annoncée. La provenance utilise les SHA-256 exacts des sources du raccordement et des verrous. Les identifiants `mockllm/model`, `orka-offline-simulation` et `simulation-only` décrivent seulement ce test logiciel ; aucun coût, token ou comportement modèle n’est mesuré.
