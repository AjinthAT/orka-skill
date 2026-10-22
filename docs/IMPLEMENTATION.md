# Implémentation de l'entreprise IA

## Version actuelle : skill, préparation, supervision et bilan local

Le point d'entrée est [SKILL.md](../.agents/skills/orka/SKILL.md). Il oriente vers les 8 équipes, leurs 28 rôles, les workflows et les modèles. Son emplacement local suit le format documenté par [OpenAI](https://learn.chatgpt.com/docs/build-skills).

Le coordinateur est l'agent qui reçoit la demande dans l'assistant hôte, par exemple Codex ou Claude Code. Il lit le skill et exécute les étapes avec les outils réellement disponibles. Quand l'utilisateur autorise une mission avec sous-agents et que l'environnement le permet, le coordinateur lance les spécialistes et leur transmet les mandats. Les fiches Markdown ne sont pas des configurations natives de processus ou de serveurs.

Les missions produit sont suivies sous `projets/<identifiant>/` et les missions transversales sous `entreprise/missions/<identifiant>/`. Le code est modifié dans le dépôt désigné. Les échanges passent par la messagerie des sous-agents ou sont relayés par le coordinateur ; les fichiers permettent une reprise dans une autre session.

Cette version décrit et guide les missions des différents services à la demande : étude, marketing, commercial, réalisation, lancement, support, finance, RH et pilotage. Le registre local ajoute la persistance en base des tâches, réservations et événements ; les connaissances métier restent dans les documents de mission. L'exécution réelle dépend des outils et du mandat disponibles. Aucun service permanent, interface, calendrier ni accès externe n'a été configuré.

## Organisation des agents dans une session

Le coordinateur reçoit la mission, choisit le workflow et répartit les tâches. Les responsables de service cadrent le travail de leurs spécialistes, relisent les sorties et échangent avec les autres services. Ces responsabilités ne nécessitent pas systématiquement un agent supplémentaire : elles peuvent être regroupées explicitement pour une petite mission.

Les 28 rôles sont un catalogue, pas une exigence de 28 exécutions simultanées. Le coordinateur réserve les places disponibles, lance les tâches prêtes, collecte leurs sorties et ouvre les suivantes. La limite par défaut de trois sous-agents s'applique à l'ensemble de l'exécution, responsables et délégations imbriquées compris.

Les fiches restent des instructions de rôle. Elles ne sont pas des fichiers natifs de configuration d'agents persistants. Le moteur futur devra les charger et appliquer leurs mandats pour créer de véritables exécutions.

## Préparation des modèles et des prompts

Le coordinateur porte maintenant la procédure de [gestion des agents](../.agents/skills/orka/references/orchestration-agents.md). Le catalogue JSON du skill associe les 28 rôles à six profils proposés ; le choix peut être adapté à la tâche avec justification. Il ne modifie pas la configuration personnelle de Codex.

L'outil [preparer_agent.py](../.agents/skills/orka/scripts/preparer_agent.py) prépare le mandat et les paramètres sans dépendance tierce. Il vérifie les champs, le rôle, le profil et la compatibilité modèle/effort connue ; avec des capacités fournies par l'appelant, il refuse aussi les réglages absents de cette déclaration. Il inclut uniquement la fiche du rôle choisi et préserve les critères. Il ne mesure pas un abonnement ni les paramètres effectivement appliqués.

La sortie contient une requête pour les champs d'un lanceur Codex compatible. Elle n'est pas une requête Claude native ; sur un autre hôte, utiliser les mandats documentaires et les outils natifs sans appliquer le catalogue Codex. Le coordinateur doit vérifier autorisations, dépendances, capacité et interface réelle avant lancement. Aucun service continu ni client API n'est ajouté par ce script. Les capacités déclarées et la validation locale ne prouvent pas qu'un modèle a été exécuté.

Les tests locaux se lancent depuis la racine avec :

```sh
python3 -B .agents/skills/orka/scripts/test_preparer_agent.py
```

Ils vérifient notamment le respect du modèle explicite, le refus d'un réglage indisponible, les critères transmis, la préparation des rôles et l'absence d'écrasement des fichiers. Ils ne constituent pas des évaluations du comportement des modèles.

La préparation version 2 conserve aussi le mode explicitement demandé, exige les entrées d'une revue/correction/reprise, distingue les tentatives d'une tâche et refuse les clés JSON dupliquées. L'empreinte de la requête complète distingue un changement de modèle ou d'effort d'un simple changement de prompt. Elle ne fournit pas de contrôle automatique des exécutions en double.

Les futures évolutions suivent [la procédure d'évaluation](../.agents/skills/orka/references/evaluation-agents.md), qui sépare les tests logiciels, la revue documentaire et les résultats réellement observés sur des modèles. Ce document tient aussi la liste priorisée des renforcements encore à implémenter.

## Supervision locale livrée

Le script [superviser.py](../.agents/skills/orka/scripts/superviser.py) fournit un registre SQLite local sans dépendance tierce. Ses transactions contrôlent capacité commune, tâches et fichiers réservés, compteurs de tentatives et événements. Les dépendances doivent être enregistrées avant leurs tâches aval. Chaque tâche conserve sa requête de référence ; une reprise ajoute le constat sans recharger silencieusement le modèle ou les instructions.

Les étapes sont distinctes : réservation, lancement extérieur et rattachement, réception du résultat, confirmation de fin du rédacteur, puis acceptation. Une réservation inactive n'est jamais libérée automatiquement. L'acceptation exige les observations de tous les critères et le fichier correspondant à l'empreinte soumise ; les dépendances sont de nouveau examinées. Les identités, constats d'arrêt et paramètres appliqués sont fournis par le coordinateur, sans vérification auprès d'un moteur externe.

Le [guide de supervision](../.agents/skills/orka/references/supervision-locale.md) décrit l'initialisation explicite, les commandes et les limites. La base n'est pas créée lors de la simple lecture de l'état ; aucune base de mission réelle n'a été initialisée pendant ce développement. Les tests utilisent des dossiers temporaires et aucun modèle.

```sh
python3 -B .agents/skills/orka/scripts/test_superviser.py
```

Cette implémentation couvre le registre local, pas le lancement automatique, un service continu ou le contrôle technique d'un outil extérieur. Les réservations n'empêchent pas un processus non enregistré d'écrire sur le disque. Le budget financier, l'annulation d'une tâche et la modification d'un mandat enregistré ne sont pas implémentés dans cette première interface.

## Pilotage renforcé

Le [pilotage des missions](../.agents/skills/orka/references/pilotage-missions.md) ajoute une organisation adaptée au résultat attendu : mission compacte, coordination entre services ou décision avec revue critique. Il définit les tâches prêtes, les responsabilités, les preuves d'acceptation et le traitement des résultats affectés par un changement.

Ces règles guident l'exécution dans la session. Les fichiers Markdown ne les imposent pas seuls. Le registre applique déjà capacité et tentatives, unicité des réservations, transitions et preuves structurées d'acceptation dans son périmètre. Les autorisations techniques et le contrôle des processus extérieurs restent à appliquer dans le moteur complet. Les appréciations éditoriales ou métier restent des revues, même si leur résultat est enregistré.

Les [processus communs](../.agents/skills/orka/references/processus-transverses.md) couvrent les événements entre les workflows : demande nouvelle, changement de périmètre, transmission, incident et clôture. La [gestion documentaire](../.agents/skills/orka/references/gestion-documentaire.md) précise les versions et les sources de référence. Ces procédures utilisent le suivi existant et n'imposent de nouvelles fiches que lorsque le cas le nécessite.

## Vision, ressources IA et identité — version 0.2.0

La fonction RH gère par défaut les ressources des agents : allocation, modèles/effort par tâche, qualification et usage observable. Le coordinateur conserve les lancements ; les identifiants des rôles restent stables. Le catalogue v2 propose le profil analyse pour la qualification, ajustable selon le travail réel. Les guides [ressources IA](../.agents/skills/orka/references/ressources-agents.md), [vision/preuves/innovation](../.agents/skills/orka/references/vision-preuves-innovation.md) et [noms/domaines](../.agents/skills/orka/references/noms-domaines.md) sont chargés selon le besoin. Les questions décisives, preuves manquantes et expériences proposées restent dans les documents existants.

Il s'agit de procédures et de profils, pas de nouveaux services : aucun collecteur de tokens, arrêt automatique sur budget, vérificateur de domaines ou apprentissage de modèle n'a été implémenté. Une vraie mesure d'usage ou vérification de disponibilité exige l'outil de l'hôte adapté ; sinon son résultat reste indisponible. Aucun domaine de projet n'a été vérifié au cours de cette maintenance.

## Version 0.3.0 : expériences et bilan des agents

Le guide [expériences et apprentissages](../.agents/skills/orka/references/experiences-apprentissage.md) relie hypothèses, tests bornés, résultats et décisions. Il distingue découverte, faisabilité et adoption, conserve les résultats inconclusifs et motifs d'abandon, puis réexamine les conclusions affectées par une preuve modifiée. Ces liens et décisions restent documentaires ; aucun moteur d'expérimentation, graphe automatique, entretien ou prototype métier n'a été exécuté pendant cette maintenance.

Le script [bilan_agents.py](../.agents/skills/orka/scripts/bilan_agents.py) est implémenté : il lit un relevé JSON fourni et produit tâches, tentatives, reprises, dénominateur d'acceptation initiale, sous-totaux de tokens connus et coûts séparés par nature/devise. Il conserve le détail des agents et la provenance fournie. Les valeurs absentes restent inconnues ; les mesures déclarées cumulatives, les doublons d'identifiants et les historiques incomplets d'une tâche incluse sont refusés. Il ne peut détecter une omission de tâche, un recouvrement dissimulé sous deux identifiants différents ou une fausse preuve textuelle.

Le [guide du bilan](../.agents/skills/orka/references/bilan-agents.md) précise la normalisation, la couverture et les limites. Ce script est indépendant du catalogue Codex et ne modifie ni données ni paramètres. Aucun collecteur, export automatique SQLite, calcul tarifaire, plafond financier ou classement automatique des modèles n'est ajouté. Les tests utilisent des mesures simulées et vérifient le fonctionnement après installation dans un autre dossier.

```sh
python3 -B .agents/skills/orka/scripts/test_bilan_agents.py
```

## Premier essai utile

La version 0.1.1 renforce la restitution après revue d'usage : synthèse dirigeant visant une page pour les études et décisions entre équipes, conclusion actuelle avant l'historique, référence unique des critères et liens relatifs entre pièces d'un dossier partageable. Les missions compactes gardent un livrable regroupé ; les étapes de découverte et de confirmation sont distinguées selon les inconnues réelles. Ces règles sont documentaires, sans nouveau moteur ni contrôle automatique de longueur. La [trace d'évaluation](../.agents/skills/orka/references/evaluation-agents.md) précise ce qui a été examiné et ce qui reste à éprouver sur d'autres missions.

Choisir un vrai projet, un marché cible et les contraintes déjà connues. Lancer le skill avec le prompt du [guide de démarrage](../README.md). Examiner ensuite le dossier : les sources justifient-elles les conclusions ? Les objections ont-elles changé quelque chose ? Le prochain test permet-il de réduire une incertitude importante ?

Faire évoluer les instructions à partir des problèmes observés. Les [scénarios de validation](../.agents/skills/orka/references/validation.md) couvrent les cas incomplets, les désaccords et les outils indisponibles.

## Évolution : une application qui pilote les agents

Pour fonctionner sans session interactive ouverte, il faudra raccorder le registre à un moteur d'exécution et à un service de suivi. Le tableau distingue les composants disponibles des fonctions encore à construire.

| Composant | Responsabilité | État |
|---|---|---|
| Réception des missions | Enregistrer demande, contexte et contraintes. | Documents et enregistrement des tâches disponibles. |
| Coordinateur | Décomposer et choisir les spécialistes. | Instructions et préparation disponibles ; rôle porté par l'agent principal. |
| Exécuteur | Lancer les agents et contrôler leurs processus. | Lancement assuré par les outils de session, pas par le registre. |
| File de tâches | Contrôler dépendances, réservations et tentatives. | Implémentée localement ; ordonnanceur automatique à construire. |
| Messagerie | Acheminer questions, objections et réponses. | Outils de session ; pas de messagerie autonome ajoutée. |
| Stockage | Conserver contexte, requêtes, événements et résultats. | Documents et registre disponibles ; pas de sauvegarde automatique. |
| Contrôle des outils | Appliquer les droits et moyens autorisés. | À raccorder au moteur ; le registre ne fournit pas un environnement isolé. |
| Suivi | Montrer états, blocages et mesures. | État, journal, alertes et bilan local des relevés fournis ; interface et collecte de coûts à construire. |

Le MVP du moteur suivrait les états tâche « à faire », « en cours », « à vérifier », « terminée », « bloquée » et « annulée ». Une correction reviendrait à « à faire » avec son motif ; un échec d'outil serait enregistré comme événement. Chaque tâche aurait un responsable, des dépendances avec versions, une sortie distincte, des critères, un responsable d'acceptation et une limite de tentatives. Le statut d'une tâche resterait distinct de la décision commerciale sur le projet.

Les messages seraient corrélés par projet, tâche et échange. Chaque opération persistante aurait un identifiant permettant de reconnaître une reprise et d'éviter de dupliquer les actions. Les livrables partagés auraient un rédacteur responsable ou un contrôle de version pour éviter les écrasements.

Le moteur vérifierait les dépendances avant lancement et réserverait les emplacements de sortie. Une réattribution ne pourrait pas laisser deux rédacteurs actifs sur le même fichier. Une entrée modifiée signalerait les résultats à réexaminer ; une acceptation se rapporterait à la version vérifiée, jamais implicitement à une version ultérieure.

Les changements, transmissions et incidents seraient liés aux missions et tâches concernées. États des documents, états des tâches et autorisations resteraient distincts. Le stockage et la sauvegarde devraient être implémentés et vérifiés avant toute promesse de restauration ; les conventions Markdown seules ne les fournissent pas.

Après interruption, le moteur relirait les états enregistrés, réconcilierait les tâches en cours et ne relancerait pas une action externe dont le résultat est incertain sans d'abord le vérifier. Les limites de coût ou de temps seraient appliquées à partir de mesures disponibles, sans annoncer une précision inexistante.

Le registre utilise SQLite localement. Le choix du client de lancement et d'un éventuel hébergement reste à faire selon le besoin réel. Les instructions, le préparateur et le registre fonctionnent sans installer de SDK ni de dépendance tierce.

La performance serait évaluée sur des missions comparables : taux d'acceptation initiale avec son dénominateur, corrections, durée et consommation disponibles. Aucune amélioration chiffrée n'est établie par la seule modification des instructions.

## Ordre de développement proposé

1. Exécuter une étude réelle avec le skill et examiner la qualité des livrables.
2. Ajuster les rôles, les échanges et les critères de sortie selon les résultats.
3. Raccorder le registre livré à un client de lancement et au suivi réel des agents.
4. Vérifier les interruptions du client, les limites de travail et le traitement des effets extérieurs incertains ; les tests locaux couvrent déjà les réservations, dépendances et tentatives.
5. Ajouter une interface de suivi si elle est utile.
6. Exécuter et éprouver les autres workflows documentés, selon les outils disponibles et les projets autorisés.

Le marketing, les ressources des agents IA et le support disposent de missions et workflows dédiés au même titre que la technique. Le moteur les active sur une mission ou un événement explicitement configuré ; les fichiers ne les font pas tourner continuellement.
