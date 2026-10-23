# Réception du transport Claude simulé

Propriétaire : coordinateur de maintenance. Version : 1. Date : 23 octobre 2026.
Mandat : contrôler le catalogue à chaque requête simulée, sans appel modèle et en préservant L4.

## Périmètre livré

Le [transport](../tools/prototype_sdk_inspect/claude_simulated.py) utilise le vrai `ClaudeSDKClient` du SDK épinglé `0.2.173`, avec un protocole de contrôle local et le routage MCP réel du SDK. Les réponses proviennent d’une liste JSON figée en mémoire. Aucun binaire Claude Code, API de modèle, mécanisme de repli fournisseur ou nouveau paquet n’est utilisé. Le [guide](ADAPTATEUR-CLAUDE-SDK.md#transport-simulé-à-chaque-génération) décrit l’interface opérateur et les limites.

Avant chaque génération fictive, le catalogue est relu par `tools/list`, validé, puis copié dans l’enveloppe sérialisée destinée au simulateur. Un second contrôle vérifie les trois noms qualifiés, leurs descriptions et schémas stricts, sans s’appuyer sur l’objet mutable reçu du serveur. Les options sont aussi revalidées avant et après la préparation. Les réponses de script visant un autre outil ne déclenchent aucune opération backend.

L’enveloppe fictive n’est pas une requête complète à une API réelle. La réception concerne le client Python et ce transport simulé ; elle ne qualifie pas le CLI, son catalogue fournisseur, un comportement modèle ou l’ensemble de P2/P3 du [plan](PLAN-PROTOTYPE-SDK-INSPECT.md).

## Tests observés

Environnement : Python 3.12.13, contrôleur macOS ARM64, dépendances Claude déjà installées dans l’environnement temporaire dédié et verrouillées lors de la réception précédente ; Docker Linux ARM64 avec image P0/P1 déjà en cache. Le transport utilise asyncio et les trames de contrôle du SDK épinglé. La suite ne télécharge rien.

La [nouvelle suite](../tests/test_claude_simulated.py) comporte **21 tests** :

| Groupe | Nombre | Contrôles |
|---|---:|---|
| Portables | 4 | Catalogue sérialisé exact ; outils supplémentaires, manquants, dupliqués, étrangers ou hébergés refusés ; changements de schémas/descriptions/enveloppe refusés ; JSON ambigu ou invalide refusé ; import sans opération externe |
| Client SDK et transport en mémoire | 15 | Routage réel des trois outils ; nouvelle lecture du catalogue à chaque génération ; injection MCP tardive et dérive après préparation bloquées ; options revalidées jusqu’au dernier point ; délai vérifié après préparation ; réponses inconnues refusées ; erreurs MCP conservées dans le contexte suivant ; copies sans partage mutable ; limite de 8 générations ; script épuisé et erreurs hôte arrêtés sans fuite de texte privé ; protocole, corrélation, délais, annulation et interdiction de réutilisation |
| Client SDK vers Docker réel | 2 | Parcours de cinq générations avec quatre opérations MCP jusqu’au fichier UTF-8 relu ; outil ajouté dans la deuxième enveloppe bloquant une écriture prévue, aucune sortie créée, une seule opération backend journalisée, arrêt confirmé |

La suite combinée `test_claude*.py` a réussi : **39 tests exécutés, aucune omission**, soit les 18 régressions de l’adaptateur précédent et les 21 nouvelles. Les tests empêchent les connexions réseau depuis Python, les processus autres que Docker dans les essais concernés et toute construction du transport SDK par défaut. Ils autorisent seulement le client SDK lié au transport local. Les générations et réponses de cette suite sont entièrement fictives.

La régression de dérive après une première génération a notamment établi : première requête acceptée et opération `lister` exécutée ; catalogue altéré avant la seconde réponse ; aucune seconde enveloppe acceptée ; aucune écriture backend. Un autre contrôle altère le catalogue MCP lui-même entre les générations. Cela vérifie une protection répétée, au-delà du contrôle de démarrage.

Les octets des enveloppes acceptées et leurs SHA-256 restent accessibles via le transport ; les verdicts n’exposent pas le texte des exceptions hôte. Les réponses MCP sont corrélées aux identifiants de contrôle et JSON-RPC. Une attente expirée ne relance pas la requête, et une réponse tardive ne reprend pas la simulation. Les workspaces de tests sont temporaires ; les reçus de fin du worker sont vérifiés avant leur nettoyage.

## Conservation et vérification du dépôt

Avant modification, un relevé a figé les empreintes de **280 fichiers** : 262 fichiers protégés suivis, dont les évaluations et ressources du skill, plus les 18 fichiers du prototype déjà présents. Leur vérification après développement constate **zéro changement**. Le nouveau transport conserve donc les sources du backend, son contrat, les cas, les verrous de dépendances et le code de l’adaptateur précédent. Les modifications documentaires décrivent ce nouveau périmètre ; les décisions et ressources L4 restent préservées.

Le vérificateur complet du dépôt a réussi : **117 tests recensés, 58 exécutés et 59 ignorés**, **513 liens locaux valides**, suites installées du skill et ZIP vérifiés. Il couvre les quatre nouveaux contrôles portables. Les 17 nouveaux tests SDK/Docker restent facultatifs dans ce passage et sont couverts par l’exécution ciblée complète ci-dessus.

## Limites

La simulation n’effectue pas d’inférence et ne mesure pas de tokens, de coût ou de qualité métier. Son `num_turns` compte des enveloppes locales acceptées ; sa durée est une durée logicielle. Le nom `orka-offline-simulation` et l’identifiant `simulation-only` n’identifient ni modèle ni session distante réelle. Les réponses hostiles ou erronées sont des séquences écrites par l’opérateur, sans preuve de comportement d’un modèle.

Le transport de simulation n’offre aucun canal réseau. Le contrôleur Python reste toutefois un processus de confiance sur l’hôte : cette livraison ne fournit pas son sandbox pour une future API réelle. Les options de CLI ne sont pas appliquées automatiquement à un transport personnalisé ; le contrôle local répété est donc réalisé explicitement. L’avertissement du SDK sur la préautorisation des trois outils MCP est attendu : leur callback de permissions n’est pas la protection utilisée pour le catalogue simulé.

Le backend conserve ses 24 requêtes, refus reçus compris, et sa procédure d’arrêt. La simulation ajoute sa borne de 8 générations et sa durée de 120 secondes, sans réinitialiser le worker. Une seule requête utilisateur est acceptée par transport. L’intégration Inspect, le parcours OpenAI Agents SDK et tout transport vers un modèle réel restent hors de cette réception.
