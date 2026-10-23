# Adaptateur Claude Agent SDK pour le backend P0/P1

Propriétaire : coordinateur de maintenance. Version : 3. Date : 23 octobre 2026.
Périmètre : raccordement logiciel hors ligne au [backend existant](PROTOTYPE-SDK-INSPECT.md), sans modifier le skill ni L4.

L’[adaptateur Python](../tools/prototype_sdk_inspect/claude_adapter.py) lie une session P0/P1 à un serveur MCP créé par le vrai Claude Agent SDK. Il expose exactement `lister`, `lire`, `ecrire`, avec les schémas stricts du contrat figé. Il prépare des options SDK ; il ne construit pas de client, ne lance pas Claude Code et n’appelle aucun modèle. Le [transport simulé](#transport-simulé-à-chaque-génération) ajouté ensuite permet un client SDK réel avec routage entièrement en mémoire. Le [raccordement Inspect](INSPECT-CLAUDE-SIMULE.md) évalue cette simulation ; le contrôle d’un transport vers un vrai fournisseur reste à réaliser.

## Dépendances distinctes

Le [verrouillage Claude](../tools/prototype_sdk_inspect/requirements-claude.lock) et sa [provenance](../tools/prototype_sdk_inspect/claude-dependency-lock.json) fixent `claude-agent-sdk==0.2.173` et `mcp==2.3.0`, avec les empreintes des dépendances transitives. La résolution universelle cible Python 3.12 ; l’exécution observée du contrôleur est macOS ARM64, avec le backend Linux ARM64 déjà fixé par P0/P1. Une résolution universelle ne prouve pas l’exécution sur toutes les plateformes.

L’installation est une préparation nécessitant le réseau ou un cache de paquets. Depuis la racine du dépôt, dans un environnement dédié, par exemple avec uv :

```sh
uv venv --python python3.12 .orka/venvs/claude
uv pip sync --python .orka/venvs/claude/bin/python --require-hashes tools/prototype_sdk_inspect/requirements-claude.lock
```

Le SDK distribue aussi un binaire Claude Code ; son installation ne signifie pas son exécution. Aucun script du prototype ne le démarre. Les verrous P0/P1 et OpenAI–Inspect sont conservés à l’identique. L’adaptateur vérifie les versions directes et l’empreinte de son propre verrou avant de réserver un worker ; il n’installe ni ne met à jour de paquet automatiquement.

## Interface opérateur

Préparer un workspace neuf avec la commande P0/P1 documentée. `open_adapter(workspace)` est une API réservée à l’opérateur de confiance ; le modèle ne choisit ni le workspace ni les racines de fichiers.

```python
from tools.prototype_sdk_inspect.claude_adapter import open_adapter

# Image Docker déjà en cache ; démarrage du seul backend de fichiers.
with open_adapter(".orka/prototype-sdk-inspect/essai-claude-neuf") as adapter:
    options = adapter.options()
    adapter.verify_options(options)
    # Configuration seulement : aucun ClaudeSDKClient/query dans cet exemple.
```

Le serveur en mémoire se trouve dans `options.mcp_servers["orka"]["instance"]`. Les noms qualifiés attendus côté Claude sont `mcp__orka__lister`, `mcp__orka__lire`, `mcp__orka__ecrire`. Les tests utilisent le protocole MCP réel en mémoire pour initialiser ce serveur, vérifier `tools/list`, puis appeler ses outils sans modèle.

`verify_catalogue(result)` vérifie une réponse réelle `tools/list` : noms, descriptions et schémas exacts, absence de doublons, d’outil supplémentaire ou de pagination non examinée. Ce contrôle ne prouve pas le catalogue qu’un CLI non exécuté transmettrait à un fournisseur. `verify_options(options)` refuse toute différence par rapport aux options restreintes, notamment l’ajout d’un serveur, une reprise de session, un changement de prompt ou de permissions. Un futur lanceur devra réappliquer ces contrôles au dernier point de transport ; copier les options dans un autre programme ne constitue pas une garantie d’isolation de ce programme.

## Transport simulé à chaque génération

Le [transport local](../tools/prototype_sdk_inspect/claude_simulated.py) implémente l’interface `Transport` du SDK épinglé, avec des files en mémoire. `simulated_client(adapter, script)` fournit un vrai `ClaudeSDKClient` auquel ce transport est obligatoirement associé. Le `connect()` de ce client initialise seulement le protocole local ; aucun CLI ou fournisseur n’est contacté. Les demandes `mcp_message` empruntent le vrai routage du SDK vers le serveur existant et les trois handlers P0/P1.

Le script est une liste JSON copiée à la construction. Chaque élément représente une réponse fictive : `{"tool": "mcp__orka__lister", "arguments": {}}`, ou `{"text": "Fin fictive"}`. Une seule requête utilisateur est acceptée par transport. Une requête utilisateur peut produire plusieurs générations simulées, chacune recevant les résultats des outils précédents.

Avant **chaque génération**, y compris celle qui termine la simulation :

1. Les options liées à la session sont revalidées et le catalogue est relu par une nouvelle requête MCP `tools/list`.
2. Les trois outils, descriptions, schémas et l’absence de pagination sont vérifiés.
3. Une enveloppe de requête fictive est sérialisée avec les trois noms qualifiés MCP, les messages et résultats précédents. Ses octets sont vérifiés à nouveau, au dernier point avant de consommer la réponse du script, contre le contrat figé indépendant du catalogue mutable.
4. Seule une réponse fictive visant l’un des trois noms peut déclencher `tools/call`. Les arguments restent validés par le serveur SDK puis par le backend. Aucun expéditeur réseau ni callback fournisseur n’est configurable.

Une dérive tardive du catalogue MCP, un outil ajouté après cette première validation, un schéma assoupli ou des options modifiées bloque la génération suivante avant la consommation du script et avant son opération de fichier. Le transport s’arrête sans repli ni relance. Les refus de protocole ou du backend sont conservés comme résultats d’outils ; ils ne deviennent pas des instructions.

Exemple opérateur, avec un workspace P0/P1 neuf déjà préparé et l’image déjà en cache :

```python
import asyncio
from tools.prototype_sdk_inspect.claude_adapter import open_adapter
from tools.prototype_sdk_inspect.claude_simulated import simulated_client

async def verifier(adapter):
    script = [
        {"tool": "mcp__orka__lister", "arguments": {}},
        {"text": "Fin de simulation"},
    ]
    async with simulated_client(adapter, script) as (client, transport):
        await client.query("Vérification logicielle sur données fictives")
        messages = [message async for message in client.receive_response()]
        assert not messages[-1].is_error
        assert len(transport.requests) == 2

with open_adapter(".orka/prototype-sdk-inspect/essai-claude-simule-neuf") as adapter:
    asyncio.run(verifier(adapter))
```

`transport.requests` retourne les copies immuables des enveloppes acceptées ; `transport.checks` fournit numéros de génération, empreintes et verdicts sans partager d’objets mutables. `status="accepte"` signifie que l’enveloppe a passé le contrôle du catalogue ; cela ne vaut pas acceptation d’un livrable ou réussite de ses opérations. Leur conservation éventuelle relève de l’opérateur ; les enveloppes peuvent contenir les pièces lues et restent privées. Le journal du backend demeure distinct. Les échanges sont corrélés par identifiants de contrôle et JSON-RPC ; les attentes MCP sont bornées à 5 secondes et à la durée restante de la session. La simulation applique 8 générations et 120 secondes au maximum, sans remise à zéro ; fermer le transport annule sa tâche locale. Le contexte de l’adaptateur conserve la procédure de confirmation de fin du worker Docker.

Le SDK avertit que la liste `allowed_tools` préautorise les trois outils et masque pour eux le callback de permissions. La protection par génération est ici effectuée par le transport, indépendamment de ce callback. Les options de CLI ne sont pas appliquées automatiquement à un transport personnalisé : ces contrôles locaux sont donc indispensables.

L’enveloppe fictive utilise `model="orka-offline-simulation"` et n’est pas une requête prête à envoyer à l’API Anthropic. La simulation exerce le client Python et le protocole de contrôle du SDK, pas le CLI Claude Code ni sa boucle interne. Elle ne prouve pas le catalogue effectivement envoyé par un CLI réel, un comportement modèle ou l’isolation complète du contrôleur. Les compteurs et la durée des messages de résultat décrivent seulement cette exécution logicielle ; tokens et coût restent absents. Voir la [réception du transport](VALIDATION-TRANSPORT-CLAUDE-SIMULE.md).

## Contrôles conservés et ajoutés

- `tools=[]` retire les outils intégrés, dont Bash/Read/Write/Edit et la délégation. Les trois noms MCP exacts sont préautorisés ; `allowed_tools` seul ne servirait pas de restriction de catalogue. Le callback de permissions refuse tout outil qui lui est soumis.
- `strict_mcp_config=True` limite les serveurs à celui fourni. `setting_sources=[]`, `skills=[]` et `plugins=[]` évitent le chargement des configurations et skills personnels ou du projet. Les instructions Orka sélectionnées restent accessibles via `lire`, dans les copies P0/P1.
- Le prompt système est explicite, le répertoire de travail du futur contrôleur est temporaire et vide, aucune session n’est reprise et la persistance de session est désactivée dans les arguments préparés. `max_turns=8` est une borne SDK préparée, pas une mesure de générations effectivement exécutées.
- Chaque handler appelle uniquement `Session.call(nom, arguments)` sur la session liée. Un verrou sérialise les appels, sans thread de travail ni second rédacteur. Les contrôles des chemins, empreintes, créations exclusives, liens physiques/symboliques et quotas restent ceux du backend inchangé.
- Les refus backend deviennent des résultats MCP `isError` avec leur code d’origine. Une exception du transport ne publie pas son texte potentiellement privé ; elle ferme le raccordement logique, sans nouvel appel ni relance automatique. La sortie du contexte confirme l’arrêt du conteneur selon la procédure P0/P1.

La validation JSON Schema du SDK peut refuser une requête avant son handler. Ces refus de protocole ne parviennent pas au compteur du worker. Les 24 requêtes autorisées par le backend incluent toujours tous les refus qu’il reçoit ; aucun compteur n’est réinitialisé par l’adaptateur.

Le serveur MCP s’exécute dans le processus opérateur de confiance et transmet les seules opérations de fichiers au conteneur. Cela ne sandboxe pas le contrôleur SDK. En particulier, `options.env={}` n’efface pas l’environnement hérité du parent. Avant toute future exécution de Claude Code, il restera à isoler ce processus et son environnement, fixer le CLI et le modèle, vérifier le catalogue effectivement transmis, les budgets et les traces. Aucun lancement modèle n’est autorisé par cette livraison.

## Tests hors ligne

La [suite ciblée](../tests/test_claude_adapter.py) sépare contrôles portables, SDK en mémoire et backend Docker réel. Le vérificateur ordinaire exécute les contrôles portables ; les autres sont ignorés sans activation explicite et ne nécessitent aucune clé API.

```sh
ORKA_CLAUDE_SDK=1 .orka/venvs/claude/bin/python -B -m unittest discover -s tests -p test_claude_adapter.py -v
ORKA_CLAUDE_SDK=1 ORKA_P01_DOCKER=1 .orka/venvs/claude/bin/python -B -m unittest discover -s tests -p test_claude_adapter.py -v
```

La seconde commande exige l’image P0/P1 déjà en cache ; elle n’effectue aucun téléchargement. Les tests bloquent les connexions réseau depuis Python, `query`, la connexion du client SDK et le démarrage de sous-processus, sauf les commandes Docker du backend dans les tests concernés. Ils inspectent aussi le constructeur d’arguments du transport du SDK épinglé, sans résoudre ni exécuter de CLI. Les workspaces et reçus des tests sont temporaires ; les assertions vérifient l’arrêt confirmé avant leur nettoyage. Voir la [réception](VALIDATION-ADAPTATEUR-CLAUDE.md).

La [suite du transport](../tests/test_claude_simulated.py) autorise le client SDK associé au transport local et piège son transport de sous-processus par défaut. Elle teste aussi les dérives entre générations et après sérialisation :

```sh
ORKA_CLAUDE_SDK=1 ORKA_P01_DOCKER=1 .orka/venvs/claude/bin/python -B -m unittest discover -s tests -p 'test_claude*.py' -v
```

L’interface de transport et les trames de contrôle du SDK peuvent évoluer ; la version épinglée reste obligatoire et toute évolution demande une nouvelle réception logicielle.

Le [raccordement Inspect](INSPECT-CLAUDE-SIMULE.md) fournit désormais un solver qui utilise ce transport et des scorers déterministes, sans génération modèle. Il conserve un verrou séparé et les sources de l’adaptateur et du transport ; ce parcours ne lance pas le CLI Claude Code.

Sources consultées le 23 octobre 2026 : [outils personnalisés](https://code.claude.com/docs/en/agent-sdk/custom-tools), [code et options du SDK Python](https://github.com/anthropics/claude-agent-sdk-python), [permissions](https://code.claude.com/docs/en/agent-sdk/permissions). Documentation recherchée via Context7 puis confrontée aux sources du paquet réellement installé.
