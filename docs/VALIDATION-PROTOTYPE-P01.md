# Réception logicielle P0 et P1 du prototype SDK Inspect

Propriétaire et vérificateur : coordinateur de maintenance, en autocontrôle. Version : 1. Date : 23 octobre 2026. Provenance : instruction de réaliser P0/P1 du [plan](PLAN-PROTOTYPE-SDK-INSPECT.md), avec préservation de L4 et sans appel modèle.

**P0 et P1 sont reçus pour le périmètre logiciel décrit ici.** Le contrat est figé et les trois opérations de fichiers sont vérifiées dans un conteneur sans réseau. La boucle Agents SDK et Inspect n’ont été ni installés ni exécutés : P2/P3 et les critères qui en dépendent restent non vérifiés.

## Livrables et références figées

| Livrable | Référence |
|---|---|
| Schémas, limites, codes de refus et image | [contract.json](../tools/prototype_sdk_inspect/contract.json), identifiant `orka-sdk-inspect-p01-v1` |
| Nouveaux cas fictifs et empreintes | [index des cas](../tools/prototype_sdk_inspect/cases/index.json), révision `p01-cases-v1` |
| Résolution commune des dépendances futures | [dependency-lock.json](../tools/prototype_sdk_inspect/dependency-lock.json) et [requirements.lock](../tools/prototype_sdk_inspect/requirements.lock) |
| Préparation et copies indépendantes | [prepare.py](../tools/prototype_sdk_inspect/prepare.py) |
| Backend Linux des trois outils | [backend.py](../tools/prototype_sdk_inspect/backend.py) |
| Démarrage, précontrôle Docker, journal et arrêt | [container.py](../tools/prototype_sdk_inspect/container.py) |
| Régressions et commandes d’utilisation | [tests](../tests/test_prototype_sdk_inspect.py) et [guide](PROTOTYPE-SDK-INSPECT.md) |

SHA-256 du contrat final : `c4a408a9d8884d0de1b238641615897bcbe1940633e78645c12e8c8e947198d6`. La suite portable vérifie cette empreinte. Le contrat, les cas et le verrouillage sont préservés byte pour byte sur les checkouts CRLF par des règles Git ciblées ; les règles existantes des captures d’évaluation sont conservées.

La résolution par uv 0.12.0 cible Python 3.12 et Linux ARM64 et fixe 96 paquets, dont `openai-agents==0.24.0` et `inspect-ai==0.3.283`. Elle établit un jeu de métadonnées de dépendances résolu, sans prouver la compatibilité d’exécution du couple SDK–Inspect. P0/P1 n’utilisent que la bibliothèque standard Python et l’image officielle fixée par digest dans le contrat. L’image et les métadonnées ont été préparées avec accès aux registres avant les essais hors ligne ; le lanceur de tests ne télécharge rien.

## Vérifications observées

Hôte opérateur : macOS ARM64, Python 3.12.13. Moteur Docker : Linux ARM64, version 29.8.2. La suite du backend est également exécutée dans l’image Python figée, réseau `none`, sans SDK, clé ou connexion à un fournisseur de modèle.

| Suite | Résultat observé | Interprétation |
|---|---|---|
| Contrat et préparation | 8 tests réussis | Schémas stricts, empreintes, cas, destinations, substitutions et copies figées |
| Backend Linux | 22 tests réussis dans le conteneur | Accès bornés, liens, substitutions, UTF-8, quotas, écritures et délais simulés |
| Intégration Docker | 5 tests réussis sur l’hôte | Contrôles effectifs, protocole, isolation entre essais, arrêt et absence de relance |

La commande avec `ORKA_P01_DOCKER=1` découvre 35 méthodes de test. Sur macOS, elle ignore les 22 méthodes Linux dans le processus hôte, puis les exécute réellement dans le conteneur par le test d’intégration prévu. Les 13 méthodes exécutées sur l’hôte et les 22 dans le conteneur ont réussi ; il ne faut pas compter l’ignorance hôte comme une absence de vérification Linux.

Les tests contrôlent notamment :

- Les noms inconnus, champs supplémentaires, clés dupliquées, mauvais types et trames multiples refusés sans opération cachée.
- Les traversées, chemins absolus, chemins Windows/réseau et sélections d’un autre essai refusés ; aucune sentinelle extérieure n’est renvoyée ou modifiée.
- Les liens symboliques, liens physiques, FIFO et parents substitués avant l’ouverture ; `openat2` assure la résolution confinée, sans repli par chemin.
- Les sources immuables, sorties créées exclusivement, révisions distinctes et relectures vérifiant les octets et empreintes.
- Une écriture partielle ou une vérification après écriture en échec sans faux reçu de succès, sans effacement et sans reprise automatique.
- Les quotas cumulatifs, les refus comptabilisés et les délais simulés entraînant la fermeture ; la fin réelle du conteneur est confirmée avant sa suppression.
- Les montages observés, l’utilisateur 65532, les capacités effectives nulles, `no-new-privileges`, les refus d’écriture hors sortie et l’erreur réseau `ENETUNREACH`.

Les contrôles Docker rejettent aussi des inspections synthétiquement altérées, par exemple un réseau activé ou un conteneur privilégié. Les tests sont des contrôles logiciels ; aucun texte hostile n’a été soumis à un modèle.

## Parcours conservés

Quatre parcours logiciels finaux distincts ont été conservés sous le dossier local ignoré `.orka/prototype-sdk-inspect/p01-final-2026-10-23-68eff9dc/`. Chaque cas contient les copies figées, les empreintes de l’implémentation, les réponses attendues privées, l’inspection du conteneur, la sonde d’isolation, les événements, la sortie et la confirmation d’arrêt. `verification.json` relie ces pièces et indique explicitement zéro appel modèle.

Les contenus écrits ont été fournis par l’opérateur depuis les fixtures : ces parcours vérifient le transport et les fichiers, pas une réponse d’agent ni une capacité de calcul du modèle. Chaque parcours inclut des refus attendus de lecture hors périmètre, d’outil inconnu et de remplacement d’une sortie. Les quatre conteneurs ont été arrêtés puis supprimés ; leurs résultats restent sur disque.

Une première série de quatre parcours, antérieure au gel final du contrat et de l’index des cas, reste conservée séparément sous `.orka/prototype-sdk-inspect/p01-reception-2026-10-23-9e5b6de3/`. Elle ne remplace pas la série finale et ne compte pas comme répétition de modèle. Le premier contrôle de lancement avait aussi révélé un import local incompatible avec `python -I` ; le chemin de code monté en lecture seule est désormais ajouté explicitement, et le parcours complet est couvert par la suite Docker.

Ces dossiers locaux ne sont pas fournis par un clone public et ne sont pas sauvegardés par Git. Les sources et tests publics permettent de créer de nouvelles preuves sans écraser ces dossiers.

## Réception par critère du plan

| Critère | État dans ce lot | Portée |
|---|---|---|
| A02–A07 | Satisfaits | Protocole, droits des fichiers, isolation système et parcours de fichiers du backend |
| A08–A09 | Partiellement vérifiés | Séparation des fichiers et refus des opérations ; contexte et comportement SDK non éprouvés |
| A01, A10 | Non vérifiés | Catalogue effectif au transport modèle, bridge et fournisseur simulé de P2/P3 |
| A11 | Partiellement vérifié | Worker, quotas, erreurs, délais simulés et arrêt des processus ; ordonnancement global encore absent |
| A12–A14 | Partiellement vérifiés | Manifeste et événements du backend disponibles ; corrélation SDK, scorers Inspect et mesures de modèle absents |
| A15 | Satisfait sur le périmètre contrôlé | L4, ressources du skill et travaux antérieurs préservés ; aucun réglage personnel modifié |

La qualification porte sur Linux ARM64 et le chemin de lancement essayé depuis macOS ARM64. Les primitives Linux incluent aussi un numéro de syscall pour x86_64, mais aucune session Docker x86_64 ou Windows n’a été qualifiée dans ce lot. Le contrôleur, le code Python, Docker et l’opérateur restent de confiance ; cette réception n’est pas une certification contre un administrateur hostile.

## Préservation et vérifications du dépôt

Les empreintes de 262 fichiers suivis ont été comparées avant et après le travail : évaluations publiques existantes, ressources du skill, documents L4 ciblés et pont MCP antérieur inchangés. Cela inclut les correctifs de supervision déjà présents au début de cette instruction. Les pièces privées/réservées, le manifeste complet, les conteneurs et les dossiers d’exécution L4 n’ont pas été utilisés.

Le prototype reste hors du ZIP du skill. Les tests portables sont automatiquement découverts par le vérificateur ; Docker reste optionnel. La vérification complète du dépôt contrôle format, liens locaux, régressions, installation déplacée et archive. Aucun test logiciel n’est présenté comme une exécution de modèle ou comme un gain de qualité ou de coût.

Suite utile : réaliser P2 avec un fournisseur simulé et un contrôle du catalogue à la dernière frontière de transport, puis P3 avec Inspect. Toute future exécution réelle exige son propre mandat et une campagne distincte de L4.
