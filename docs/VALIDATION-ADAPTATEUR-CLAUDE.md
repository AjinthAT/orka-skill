# Réception logicielle de l’adaptateur Claude

Propriétaire : coordinateur de maintenance. Version : 1. Date : 23 octobre 2026.
Mandat : ajouter le [raccordement Claude Agent SDK](ADAPTATEUR-CLAUDE-SDK.md) au backend P0/P1, avec trois outils et tests hors ligne, en préservant L4.

## Résultat observé

L’adaptateur utilise réellement `create_sdk_mcp_server` de `claude-agent-sdk==0.2.173` avec `mcp==2.3.0`. Le serveur MCP, ses schémas et ses réponses ont été exercés en mémoire. Les opérations de fichiers ont aussi traversé ce serveur vers les vraies sessions Docker P0/P1. Aucun client Claude n’a été connecté, aucun binaire Claude Code démarré, aucun appel modèle exécuté.

Les dépendances Claude ont été téléchargées puis installées dans un environnement temporaire dédié, distinct du dépôt, avec vérification du [verrouillage](../tools/prototype_sdk_inspect/requirements-claude.lock). Cette préparation réseau précède les tests hors ligne. Le SDK inclut un binaire CLI qui n’a pas été exécuté. Aucun paramètre personnel n’a été changé.

Environnement observé : contrôleur Python 3.12.13 sur macOS ARM64 ; backend Docker Linux ARM64, image P0/P1 déjà en cache. Le contrat garde l’empreinte `c4a408a9d8884d0de1b238641615897bcbe1940633e78645c12e8c8e947198d6`. Ses sources `prepare.py`, `container.py`, `backend.py`, `contract.py`, ses cas et son verrou OpenAI–Inspect n’ont pas été modifiés par ce raccordement.

## Vérifications

La [suite Claude](../tests/test_claude_adapter.py) compte **18 tests réussis, sans omission** lorsque les deux options SDK et Docker sont activées :

| Groupe | Nombre | Résultat vérifié |
|---|---:|---|
| Portable | 3 | Contrat et verrou distincts, import sans opération externe, dérive de dépendance refusée avant démarrage du worker |
| SDK réel en mémoire | 11 | Catalogue et schémas exacts ; outils inconnus, champs supplémentaires et types invalides refusés ; routage des trois handlers ; erreurs backend conservées ; exceptions hôte masquées et arrêt logique ; options isolées et modifications refusées ; arguments CLI préparés sans exécution ; fermeture et liaison d’essai |
| MCP vers Docker réel | 4 | Inventaire sans grille privée ; pièces hostiles servies comme données ; traversées et écritures sur entrées refusées ; création UTF-8 vérifiée et remplacement refusé ; séparation des essais ; liens insérés après démarrage refusés ; quota backend conservé ; arrêt confirmé et essai non réutilisable |

Les tests patchent les points d’entrée modèle du SDK, les connexions réseau depuis Python et le démarrage des processus. Seules les commandes Docker opérateur sont permises dans le groupe Docker. Le constructeur d’arguments interne du SDK épinglé est inspecté sans lancement : il conserve `--tools ""`, les trois noms MCP exacts, `--setting-sources=`, `--strict-mcp-config` et `--no-session-persistence`.

La suite P0/P1 existante a aussi été relancée avec Docker : **35 tests recensés, 13 exécutés sur l’hôte et 22 ignorés sur macOS**. L’un des 13 tests exécute les **22 régressions Linux du backend dans le conteneur**, toutes réussies. Aucun conteneur portant l’étiquette du prototype ne subsiste après ces vérifications.

Le vérificateur complet du dépôt a réussi séparément, sans dépendance Claude obligatoire : **96 tests recensés, 54 exécutés et 42 ignorés** selon plateforme et activation. Les trois tests portables Claude y sont inclus ; les 15 tests SDK/Docker y sont volontairement ignorés et couverts par la suite ciblée ci-dessus. Les installations déplacées, suites du skill et archive distribuable ont réussi leurs contrôles.

Un relevé des empreintes de **262 fichiers protégés suivis**, dont `evals/**`, `.agents/**`, les décisions L4 et le raccordement L4, a été établi avant modification puis vérifié : **aucun changement**. Les corrections de réservation déjà présentes dans `superviser.py` et ses tests sont conservées ; elles ne font pas partie de ce nouvel adaptateur.

## Limites et suite éventuelle

Cette réception porte sur le logiciel, ses options et son protocole MCP. Elle ne qualifie ni le comportement d’un modèle Claude, ni le catalogue réellement transmis par un CLI en cours d’exécution, ni l’intégration Inspect. Le contrôleur SDK n’est pas sandboxé par le conteneur de fichiers ; son environnement hérité, sa configuration effective et ses éventuels accès devront être contrôlés avant un futur lancement autorisé.

Les 24 requêtes et les refus comptés par le backend restent inchangés. Un refus JSON Schema propre au protocole MCP peut intervenir avant le handler et ne consomme alors aucune requête du worker. La borne SDK `max_turns=8` est seulement préparée ; aucun comptage réel de générations, consommation ou coût n’a été observé. Les reçus des tests temporaires ont été contrôlés avant nettoyage ; les journaux de réception ne constituent pas des exécutions L4.
