# Coordinateur : responsable des agents

Le rôle `coordinateur` existant assure aussi la gestion des agents. Il ne faut pas créer un second directeur chargé de refaire son travail. Par défaut, l'agent principal porte ce rôle ; les spécialistes exécutent des mandats bornés. Un responsable métier peut organiser ses livrables sans devenir un processus supplémentaire.

La fonction RH IA conseille allocation, qualification et suivi des ressources selon [ressources-agents.md](ressources-agents.md). Le coordinateur conserve lancement, accès, capacité commune et propriétaires des fichiers. Le suivi des tokens dépend de mesures réellement exposées ; ni le préparateur ni le registre n'en ajoutent automatiquement.

## Boucle de gestion

1. Lire la demande, l'état et les décisions utiles. Identifier le résultat, les dépendances, le périmètre autorisé et les moyens réellement disponibles.
2. Préparer les tâches selon [le pilotage](pilotage-missions.md). Pour chaque délégation, choisir rôle, profil modèle/effort, contexte minimal, sortie distincte et responsable d'acceptation.
3. Construire le mandat selon [le prompting](prompting-agents.md). Vérifier les réglages avec [la politique des modèles](modeles-effort.md). Un bon modèle ne compense pas une tâche sans objectif ni preuve attendue.
4. Réserver une place dans la capacité globale, puis lancer seulement les tâches prêtes. Garder le travail de synthèse et les décisions communes dans l'agent principal. La capacité de trois sous-agents reste un plafond, pas une obligation.
5. Recueillir les résultats et questions ; poursuivre les tâches indépendantes pendant l'attente. Une tâche bloquée indique le besoin exact et la personne ou source nécessaire. Un silence n'est pas une réussite.
6. Faire vérifier les critères, transmettre les corrections ciblées ou accepter la version effectivement examinée. Ouvrir les tâches dépendantes quand leurs entrées sont utilisables.
7. Terminer par les livrables, limites et suites. Conserver l'état de reprise et libérer les spécialistes devenus inutiles selon les contrôles disponibles.

## Gestion des agents et des tentatives

Le [registre local](supervision-locale.md) met en œuvre la persistance des tâches et réservations lorsqu'il est utilisé. La réservation précède le lancement et le rattachement de l'agent réel. La fin d'un délai déclenche une vérification, pas une libération automatique. Tous les coordinateurs partageant une capacité doivent utiliser la même base.

Le suivi relie mission, tâche, tentative, rôle, identifiant réel d'agent, état, profil demandé, modèle/effort demandés, valeurs appliquées si observables, fichiers possédés et empreintes du prompt et de la requête. Une nouvelle tentative utilise son propre identifiant de lancement sans perdre le lien à la tâche. Tant qu'aucun lancement n'a eu lieu, l'état reste préparé et l'identifiant réel reste absent.

Une empreinte reconnaît le contenu préparé ; elle ne prouve pas l'exécution ni ne garantit à elle seule qu'une action ne sera pas exécutée deux fois. Le contrôle des tentatives et des effets reste à appliquer par le coordinateur et le futur moteur.

Réutiliser un agent pour poursuivre la même tâche si son contexte et ses paramètres restent adaptés. Une instruction de correction ne change pas implicitement son modèle. Si un autre modèle est nécessaire et que l'outil ne peut pas modifier l'agent existant, arrêter ou attendre l'ancien rédacteur, conserver la trace et lancer une nouvelle tentative avec contexte explicite. Le propriétaire des fichiers doit rester unique.

Les spécialistes ne lancent pas de descendants sans allocation du coordinateur et autorisation applicable. Les limites de concurrence et de tentatives restent globales. Une tâche nouvelle ne constitue pas une raison de recopier tout l'historique dans un nouvel agent.

## Préparation locale des requêtes

Le script [preparer_agent.py](../scripts/preparer_agent.py) prépare un prompt complet et des paramètres de lancement à partir d'un mandat JSON. Il inclut uniquement les consignes communes, la fiche du rôle choisi et le contexte fourni. Le catalogue [profils-modeles.json](profils-modeles.json) contient les propositions de réglage et la correspondance des 28 rôles.

Le script n'appelle aucun modèle, ne lance aucun agent et ne vérifie pas un abonnement. Le coordinateur reste responsable de la disponibilité des outils, des modèles, des accès et du lancement effectif.

Dans l'environnement actuel, la requête correspond aux champs de `collaboration.spawn_agent` : `task_name`, `message`, `fork_turns`, `model` et `reasoning_effort`. Lorsqu'un réglage explicite est utilisé avec cet outil, le contexte est fourni dans le message et `fork_turns` vaut `none`. La prise en charge doit être réexaminée si l'interface change.

Sans possibilité de régler modèle/effort, utiliser uniquement le mode réellement proposé par l'environnement et signaler l'héritage ou la limite. Ne pas déclarer appliqué un réglage présent seulement dans le texte du prompt.

## Gestion de la mémoire

Conserver objectifs, décisions et liens dans la mémoire commune. Les spécialistes reçoivent les pièces nécessaires à leur tâche, les versions, les contraintes et les dépendances, sans données client ou RH sans rapport avec leur mission. Les journaux techniques volumineux restent dans leurs fichiers ; les retours portent sur preuves et conclusions utiles.

Une source contradictoire déclenche une vérification ciblée ; une nouvelle information ne justifie pas de refaire tout le dossier. La reprise d'un agent inclut ce qui a changé, ce qui reste valide, la version courante et le point d'arrêt.

Pour un manque décisif, appliquer le [protocole de complément borné](prompting-agents.md#compléter-le-contexte-par-passes-bornées). Le coordinateur conserve le compteur commun de la tâche à travers les tentatives et transmet seulement la réponse pertinente et autorisée, avec provenance et version. Un accès refusé ou une limite atteinte conduit à un résultat partiel explicite. À la reprise, transmettre aussi les demandes déjà consommées, les sources remplacées et les conclusions à réexaminer ; conserver les paramètres modèle/effort, sauf changement explicite compatible avec le mandat.
