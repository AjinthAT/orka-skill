# Collaboration et débats

## Exécution réelle

Utiliser les outils de sous-agents disponibles dans la session lorsque cette délégation est autorisée. Ne pas faire passer un message d'agent pour une autorisation humaine. Les instructions de ce document ne remplacent pas les règles d'autorisation de l'environnement.

Par défaut, limiter à trois sous-agents simultanés sur toute la mission, responsables et délégations imbriquées compris, ou moins si la capacité ou les consignes l'imposent. Le coordinateur répartit ces places entre les équipes et met les autres tâches en attente. Un rôle n'implique pas un processus permanent ; libérer les spécialistes après leur livrable.

Sans sous-agents, appliquer les analyses successivement en annonçant ce mode. Ne pas fabriquer de conversation à plusieurs ou qualifier les résultats de vérification indépendante.

## Mandat d'un spécialiste

Transmettre les éléments suivants à chaque lancement :

- Identifiant de mission et de tâche ; rôle, objectif concret et responsable unique du résultat.
- Brief, contraintes et faits disponibles ; seulement les pièces utiles au passage courant.
- Fichier de sortie distinct par tâche, dont il est seul responsable ; utiliser l'identifiant de tâche dans le nom pour éviter les collisions entre agents du même rôle.
- Outils et actions autorisés par la session, ainsi que les limites de travail connues.
- Résultat attendu, critères vérifiables, responsable d'acceptation, dépendances et versions des entrées.
- Instruction de distinguer sources, estimations, hypothèses et questions.

Pour les analyses et propositions à confronter, le premier passage ne reçoit pas les recommandations des autres spécialistes. Pour une tâche dépendante, transmettre au contraire le livrable amont nécessaire : le frontend a besoin du design et des contrats, le rédacteur du brief marketing. L'indépendance des avis ne doit pas supprimer les dépendances du travail.

Chaque transmission indique le livrable, sa version ou date, les points vérifiés, les questions ouvertes et le responsable attendu. Le destinataire vérifie qu'il peut travailler avec ces entrées et signale les manques ; le coordinateur actualise les dépendances. Une entrée modifiée entraîne le réexamen des seules tâches affectées selon [le pilotage des missions](pilotage-missions.md).

## Échanges entre agents

Un spécialiste peut poser une question, demander une preuve, formuler une objection ou proposer une correction. Utiliser la messagerie réelle entre sous-agents si elle existe et est permise ; sinon, le coordinateur transmet les messages. Ne pas supposer qu'un fichier Markdown envoie une notification.

Format d'un échange utile :

| Champ | Contenu |
|---|---|
| Identifiant | Référence unique dans le projet, par exemple E-001. |
| Auteur et destinataire | Rôles réellement mobilisés. |
| Type | Question, objection, preuve, réponse ou proposition. |
| Sujet | Conclusion ou hypothèse concernée. |
| Contenu | Point précis, justification et éventuelle source. |
| Résultat attendu | Réponse ou vérification qui permet d'avancer. |
| Statut | Ouvert, répondu, intégré ou désaccord maintenu. |

Les spécialistes transmettent au coordinateur les conclusions affectant le plan, les désaccords et les blocages. Regrouper les questions destinées au même agent ; une question déjà ouverte garde son identifiant et reçoit une réponse au lieu d'être dupliquée. Une notification sans conséquence sur le travail n'appelle pas une réponse de pure forme.

Consigner les éléments utiles à la décision, pas des raisonnements internes détaillés ni des dialogues décoratifs. Le coordinateur consolide par étape plutôt que de recopier chaque message dans tous les documents.

## Débat borné

1. Le coordinateur choisit les sujets susceptibles de changer la décision.
2. Premier tour : objections et demandes de preuves, regroupées par sujet.
3. Second tour : réponses, vérifications et corrections.
4. Clôture : conclusion, incertitude persistante ou test nécessaire.

En [mode autonome](autonomie.md#arbitrer-puis-agir), nommer le juge et la délégation couvrant son verdict. Pour un choix délégué, le verdict entraîne la prochaine action autorisée ; ne pas renvoyer systématiquement l'arbitrage à l'utilisateur. Le débat ne modifie ni critères d'acceptation, ni autorisations, ni budgets.

Deux tours constituent le défaut, modifiable par la mission. Une vérification ciblée supplémentaire n'ouvre pas une discussion illimitée. Sans preuve nouvelle, conserver le désaccord et terminer la synthèse. L'accord de plusieurs agents ne remplace pas une source ou un résultat terrain.

## Mémoire et fichiers partagés

Le coordinateur est seul responsable des fichiers partagés. Chaque spécialiste écrit le livrable de sa tâche ; une autre personne propose une correction sans modifier son fichier pendant son travail. Avant de réattribuer une tâche, obtenir l'arrêt ou la fin de son ancien rédacteur. Un résultat reçu tardivement reste une proposition à intégrer, sans écraser la version acceptée.

Les sources doivent rester identifiables dans chaque analyse avant consolidation. Dans le registre commun, fusionner les doublons par URL, garder le contexte et la date de consultation et signaler les contradictions. Deux articles reprenant la même étude ne sont pas deux preuves indépendantes.

Après chaque étape terminée, enregistrer les livrables disponibles, les tâches restantes et le prochain responsable. À la reprise, vérifier que les fichiers annoncés existent. La mémoire écrite conserve le contexte ; elle ne relance rien toute seule.

## Échecs et limites

En cas d'échec technique transitoire sans effet extérieur incertain, tenter au plus une reprise ciblée dans les limites de la mission. Si l'obstacle persiste, consigner la limite, poursuivre les travaux indépendants et ajuster la conclusion. Ne pas relancer une action dont l'effet est inconnu avant d'en vérifier le résultat ; ne pas contourner un refus d'autorisation par une autre méthode.

Ne pas annoncer un coût exact si l'environnement ne fournit pas cette mesure. Les limites explicites de budget et de durée du dirigeant priment sur les valeurs par défaut de ce protocole.

Arrêter les travaux lorsque les livrables sont prêts, que les limites sont atteintes ou qu'aucune progression utile n'est possible sans une information nécessaire. Expliquer alors précisément ce qui manque et enregistrer un état de reprise fidèle.

## Actions extérieures

Exécuter la mission demandée : étude, contenus, code ou suivi selon son périmètre. Contacter un client, envoyer un message, acheter un service, publier ou déployer exige une autorisation couvrant cette action. Réutiliser les autorisations déjà données ; une simple discussion entre agents ne les élargit pas.
