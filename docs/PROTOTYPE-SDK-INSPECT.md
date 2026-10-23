# Utiliser le backend hors ligne du prototype SDK Inspect

Propriétaire : coordinateur de maintenance. Version : 4. Date : 23 octobre 2026. Périmètre : P0 et P1 du [plan](PLAN-PROTOTYPE-SDK-INSPECT.md), avec renvoi au raccordement Claude, à sa simulation et à son intégration Inspect facultative. Voir la [réception logicielle](VALIDATION-PROTOTYPE-P01.md) pour les résultats et les limites.

Le backend P0/P1 fige quatre cas fictifs nouveaux et fournit les trois opérations `lister`, `lire`, `ecrire`. Il utilise uniquement la bibliothèque standard Python et Docker. Il ne charge aucun SDK, n’exécute aucun modèle et ne raccorde aucune ressource L4. Ses extensions Claude et Inspect sont des modules facultatifs distincts ; les étapes P2/P3 du parcours OpenAI Agents SDK restent à réaliser.

Un [adaptateur Claude Agent SDK facultatif](ADAPTATEUR-CLAUDE-SDK.md) réutilise ce backend sans modifier son contrat ni ses sources. Il fournit un serveur MCP en mémoire et des options SDK restreintes, testés hors ligne ; il n’ajoute pas de lanceur de modèle ni l’intégration Inspect. Son verrouillage de dépendances est séparé de celui de P0/P1.

## Contrat figé

Le [contrat version 1](../tools/prototype_sdk_inspect/contract.json) fixe schémas, codes de refus, quotas et image. Les [cas et leurs empreintes](../tools/prototype_sdk_inspect/cases/index.json) ont leur propre révision. Un cas modifié sans mise à jour des empreintes est refusé lors de la préparation ; une évolution volontaire des cas doit recevoir une nouvelle révision explicite.

La [résolution des dépendances](../tools/prototype_sdk_inspect/dependency-lock.json) cible Python 3.12 et Linux ARM64 : `openai-agents==0.24.0`, `inspect-ai==0.3.283`, 96 paquets dans le [verrouillage avec empreintes](../tools/prototype_sdk_inspect/requirements.lock). Cette résolution commune de métadonnées ne prouve pas leur compatibilité d’exécution ; aucun paquet SDK/Inspect n’a été installé ou importé pour P0/P1. Leur essai appartient à P2/P3. `requirements.in` sert à une future révision, pas à une mise à jour automatique du verrouillage.

L’image backend officielle est fixée par digest dans le contrat et n’inclut pas ces dépendances. La cible qualifiée est Linux ARM64 avec `openat2` disponible ; le lanceur Docker a été essayé depuis macOS ARM64. Aucun repli vers les accès fichiers de l’hôte n’existe si Docker ou `openat2` est indisponible.

## Préparer un essai neuf

Depuis la racine du dépôt, avec Python 3.12 et un moteur Docker local disponible :

```sh
mkdir -p .orka/prototype-sdk-inspect
python3.12 -B -m tools.prototype_sdk_inspect.prepare --case complet --destination .orka/prototype-sdk-inspect/essai-complet-01
```

Autres cas : `manquant`, `contradiction`, `hostile`. La préparation copie des entrées et instructions Orka sélectionnées, sans liens physiques ni symboliques. Elle écrit un manifeste d’accès pour le backend, et garde réponses attendues, verrouillage et provenance dans `controle/`, hors des montages de l’agent. Chaque copie porte une empreinte ; une destination existante, même vide ou symbolique, est préservée.

```text
essai-complet-01/
  inputs/       copies des seules sources et instructions autorisées
  outputs/      sorties propres à cet essai
  runtime/      backend, contrat et manifeste d’accès seulement
  controle/     grille fictive, manifeste complet, reçus et journal opérateur
```

Les fichiers `inputs` sont montés en lecture seule ; seuls les chemins logiques du manifeste sont lisibles. Les écritures sont limitées à `sorties/livrable.json`, `sorties/livrable-v2.json` et `sorties/note.md`. Une sortie n’est lisible par les outils qu’après création vérifiée dans le même processus. Les fichiers ne sont jamais interprétés comme du code.

## Exécuter des opérations logicielles

L’image doit être présente avant les tests. Le lanceur utilise `--pull=never` et ne télécharge rien. Si nécessaire, sa préparation explicite requiert le réseau :

```sh
docker pull python@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704
```

Le canal accepte un objet JSON UTF-8 par ligne, sans champ de commande ou de sélection d’essai :

```sh
python3.12 -B -m tools.prototype_sdk_inspect.container --workspace .orka/prototype-sdk-inspect/essai-complet-01 <<'JSON'
{"outil":"lister","arguments":{}}
{"outil":"lire","arguments":{"chemin":"entrees/fiche.md"}}
{"outil":"ecrire","arguments":{"chemin":"sorties/note.md","contenu":"Vérification logicielle, sans modèle."}}
{"outil":"lire","arguments":{"chemin":"sorties/note.md"}}
JSON
```

Ce sont des requêtes fournies par l’opérateur. Leur réussite ne mesure pas le comportement d’un agent. La sortie standard contient les résultats `ok`, `code`, `donnees` ; les refus n’exposent pas les chemins hôte. Les erreurs de démarrage ou de protocole terminent le client avec le code 2. Un refus métier ordinaire figure dans le résultat de l’opération ; le code de sortie du client ne vaut pas réception de tous les critères.

Avant la première opération, le lanceur vérifie les copies figées, le digest et l’architecture de l’image, les trois montages exacts et les restrictions Docker effectives. Une sonde logicielle de confiance vérifie aussi utilisateur, capacités, `no-new-privileges`, lecture seule, absence de socket Docker et réseau inaccessible. Cette sonde interne n’est pas un quatrième outil et n’est pas commandable par le modèle.

La sortie racine du conteneur est en lecture seule ; les capacités Linux sont supprimées ; le réseau et l’IPC sont désactivés ; mémoire, CPU, processus et espace temporaire sont bornés. Les ouvertures utilisent `openat2` avec confinement sous le descripteur racine, interdiction des liens et des traversées de montages. Les fichiers doivent être ordinaires et sans lien physique supplémentaire. Les lectures contrôlent les empreintes et les écritures utilisent une création exclusive puis une relecture vérifiée.

## Reprise et preuves

Chaque workspace est à usage unique. `controle/started.json`, créé exclusivement avant le lancement, interdit une seconde session qui remettrait les compteurs à zéro. En cas d’incertitude, conserver ce reçu et préparer un autre essai explicitement ; ne pas le supprimer pour relancer automatiquement une écriture.

`container-before.json` conserve la configuration Docker observée ; `isolation.json`, les résultats de la sonde ; `events.jsonl`, les réponses corrélées avec l’identifiant d’essai, leur séquence et l’empreinte de la requête. Le journal conserve notamment tailles et empreintes des fichiers effectivement servis. Il ne prouve pas la compréhension d’une pièce par un modèle.

À la fermeture, le lanceur attend la fin du rédacteur, arrête si nécessaire le seul conteneur qu’il a identifié et vérifié par son étiquette, conserve `stopped.json`, puis supprime ce conteneur. Une erreur empêchant la confirmation de fin ne libère pas l’essai pour une nouvelle session. Une écriture interrompue reste sur disque, sans reçu de succès ni effacement automatique. Les répertoires de résultats restent conservés.

Les limites du worker sont celles du contrat : 24 requêtes, refus compris, 120 secondes de session, 5 secondes par opération, 1 Mio par lecture, 64 Kio par écriture et 256 Kio écrits au total. Le worker est séquentiel ; l’ordonnancement global des agents et des essais appartient à P2. Le journal et les copies locales sous `.orka/` sont ignorés par Git et ne constituent pas une sauvegarde.

## Vérifier sans modèle

Les contrôles portables sont inclus dans le vérificateur du dépôt. Les tests Linux du backend s’exécutent directement sur un hôte compatible et sont ignorés sur les autres plateformes. La suite Docker est volontaire : elle ne dépend pas d’un téléchargement et fonctionne sans SDK ni clé.

```sh
python3.12 -B -m unittest discover -s tests -p test_prototype_sdk_inspect.py -v
ORKA_P01_DOCKER=1 python3.12 -B -m unittest discover -s tests -p test_prototype_sdk_inspect.py -v
```

La seconde commande lance également les régressions Linux dans un conteneur sans réseau. Le montage du fichier de tests dans ce conteneur relève de la vérification opérateur ; il n’est jamais ajouté aux trois montages des sessions de production. Chaque conteneur de test possède son propre nom et son étiquette pour permettre un nettoyage ciblé.

Le [transport Claude simulé](ADAPTATEUR-CLAUDE-SDK.md#transport-simulé-à-chaque-génération) vérifie désormais le catalogue à chaque génération fictive. Le raccordement OpenAI Agents SDK, son intégration Inspect et le contrôle d’un fournisseur réel restent à réaliser ; paramètres appliqués et consommation des modèles ne sont pas mesurés. Ni les fixtures ni les tests adverses n’établissent une résistance comportementale d’un modèle aux instructions hostiles.

La [simulation Claude raccordée à Inspect](INSPECT-CLAUDE-SIMULE.md) dispose maintenant de ses propres solver, scorers et traces locales, avec génération modèle interdite. Cette extension conserve P0/P1 et son verrou ; elle ne qualifie pas l’intégration OpenAI Agents SDK ni un transport vers un fournisseur réel.

Références : [Docker create](https://docs.docker.com/reference/cli/docker/container/create/), [réseau none](https://docs.docker.com/engine/network/drivers/none/), [openat2](https://man7.org/linux/man-pages/man2/openat2.2.html). Documentation vérifiée le 23 octobre 2026 ; les contrôles observés sont détaillés dans le rapport de réception.
