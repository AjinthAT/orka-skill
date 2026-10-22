# Workflow : de l'idée au dossier de décision

## 1. Cadrer

Le coordinateur reformule l'idée, le problème, les utilisateurs, l'acheteur, la zone visée et les contraintes. Il sépare décisions, informations fournies et hypothèses. Il relève seulement les questions qui changent l'analyse et poursuit ce qui peut l'être sans réponse.

Préparer le brief, le plan et l'état à partir des [modèles](modeles.md), regroupés si le niveau de mission le permet. Identifier la prochaine décision utile et les inconnues qui peuvent la changer ; choisir les documents et analyses nécessaires à cette décision. Dans le plan, choisir les spécialistes et noter les limites d'exécution : concurrence autorisée, nombre de tours, limites de temps ou de coût lorsqu'elles sont disponibles. Une limite inconnue ne devient pas un budget inventé.

Sortie : mission compréhensible et périmètre de recherche déclaré. Sans projet identifiable, rester au cadrage et demander l'idée.

## 2. Produire les analyses initiales

Répartir les questions utiles entre marché, concurrence, produit, CTO et finance. Fusionner ou omettre un rôle si le projet ne justifie pas une mission distincte ; expliquer la couverture retenue dans le plan.

Pour le premier passage, fournir à chacun le même brief, les faits établis et les contraintes, sans la recommandation des autres spécialistes. Les premières propositions produit et financières peuvent rester conditionnelles. Après ce passage, le produit et la finance doivent intégrer les dépendances réellement nécessaires.

Chaque spécialiste écrit uniquement son fichier `analyses/<tache>-<role>.md` ou renvoie son résultat au coordinateur s'il ne peut pas écrire. Chaque fait externe significatif inclut une source consultée et une date. Les spécialistes déclarent leurs éventuels accès manquants.

Commencer par la conclusion et les preuves propres à la spécialité. Relier le contexte commun plutôt que le recopier ; conserver les développements nécessaires à la vérification sans répéter les mêmes réserves dans toutes les sections.

Pour une étude concurrentielle, comparer des offres aux conditions équivalentes : devise, taxe connue ou inconnue, période de facturation et restrictions. Pour les estimations, donner formules et hypothèses. Une multiplication d'hypothèses ne devient pas une donnée de marché.

Sortie : analyses disponibles, limites explicites, questions importantes identifiées. Un échec de recherche ne doit pas être présenté comme une absence de demande ou de concurrence.

## 3. Examiner et débattre

L'évaluateur critique lit les analyses terminées et soulève les objections qui peuvent changer la recommandation. Les spécialistes peuvent également adresser une question précise à un autre spécialiste.

Appliquer [le protocole de collaboration](collaboration.md) : un premier tour d'objections, puis un tour de réponses et corrections par défaut. Le coordinateur peut organiser une vérification ciblée si elle est décisive et tient dans les limites de la mission. Éviter les discussions sans information nouvelle.

Les analyses révisées montrent d'abord la conclusion actuelle et expliquent les corrections. Conserver la conclusion initiale dans un historique daté ou une version antérieure reliée, séparée des règles courantes. Le coordinateur consigne les échanges utiles, les sources et les désaccords restants. Chaque critère retenu renvoie à une référence unique ; les variantes retirées portent le statut historique, pas celui d'une deuxième règle applicable.

Sortie : objections traitées ou explicitement ouvertes ; pas de consensus forcé.

## 4. Proposer un test terrain

Pour les inconnues critiques, définir une expérience proportionnée : entretien, démonstration, prototype, test d'usage ou offre pilote. Préciser l'hypothèse, la cible, la mesure, un seuil proposé avant le test et l'effet du résultat sur la décision.

Si fréquence du problème, capacité d'action ou intérêt de l'acheteur sont encore inconnus, privilégier d'abord une découverte bornée et son bilan. Séparer cette prochaine expérience des essais techniques ou confirmatoires ultérieurs. Leurs calculs et seuils détaillés restent en annexe conditionnelle lorsqu'ils sont utiles ; ne pas les présenter comme un programme déjà décidé ni supprimer une analyse nécessaire à une décision à fort impact. Justifier les seuils proposés et conserver les exigences de sécurité ou de droits indépendamment de la taille du test.

Sans accès à de vrais clients ni résultats transmis, livrer le protocole et marquer le test « non réalisé ». Ne pas envoyer d'invitations, publier de page ou lancer de campagne à partir de la seule demande d'étude.

Sortie : prochain apprentissage recherché et critère de décision mesurable, ou justification de l'absence de test nécessaire.

## 5. Consolider

Le coordinateur produit le dossier et recommande l'une des options : poursuivre, modifier, tester davantage ou abandonner. Une recommandation défavorable est une sortie valide.

Ouvrir la remise par `synthese.md`, selon le [modèle d'une page](modeles.md#synthesemd), ou par une section équivalente du livrable compact. Le dossier détaillé apporte les preuves et variantes ; la synthèse indique la décision attendue maintenant et une prochaine expérience proportionnée. Les travaux ultérieurs conditionnels ne deviennent pas une nouvelle mission autorisée.

Le dossier doit permettre de comprendre :

- Qui rencontre le problème et qui pourrait payer.
- Quelles preuves existent et lesquelles manquent.
- Quelles alternatives existent déjà et quelle différence est proposée.
- Quelle première version pourrait tester la proposition de valeur.
- Quelles contraintes techniques et économiques pèsent sur le projet.
- Quels risques et désaccords peuvent changer la recommandation.
- Quelle prochaine action est proposée et comment son résultat sera évalué.

Si les données manquent pour un chiffre ou une conclusion, l'écrire. Vérifier la cohérence entre périmètre produit, effort, coûts, acquisition et revenus.

Sortie : dossier traçable et état mis à jour. « Dossier remis » signifie étude livrée, pas projet validé ou lancement autorisé.

## 6. Reprendre ou passer à la réalisation

À la reprise, relire l'état, le brief et les décisions avant de relancer les tâches. Réutiliser les livrables valides et réexaminer seulement ce que de nouvelles informations remettent en cause.

Une décision explicite du dirigeant peut ouvrir une mission de prototype, marketing ou réalisation. La décrire avec ses critères d'acceptation avant d'exécuter les changements autorisés. Utiliser alors les [workflows d'entreprise](workflows-entreprise.md) et adapter les procédures techniques au dépôt et au projet réels.
