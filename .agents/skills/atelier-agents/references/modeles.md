# Modèles de livrables

Créer les documents au moment où ils deviennent utiles. Remplacer les champs indicatifs ; utiliser « inconnu », « non vérifié » ou « non réalisé » quand c'est la réalité. Les modèles ne sont pas des résultats d'étude.

## Mission compacte

Pour un résultat simple sans coordination entre services, un seul `mission.md` ou une entrée du suivi existant suffit : objectif, responsable, entrées utiles, résultat, critères contrôlés, limites et suite. Ne pas créer des fichiers vides de plan, sources, échanges ou décisions sans utilité. Appliquer [le niveau d'effort adapté](pilotage-missions.md).

## Organisation d'une mission entre équipes

Pour une mission produit, utiliser la structure ci-dessous. Pour les missions transversales, placer les documents de suivi sous `entreprise/missions/<identifiant>/`. Réutiliser les dossiers existants et ne créer que les documents nécessaires.

```text
projets/<identifiant>/
  brief.md
  plan.md
  etat.md
  analyses/
    <tache>-<role>.md
  livrables/
    <equipe>/<tache>-<document>.md
  sources.md
  echanges.md
  decisions.md
  dossier.md
```

## brief.md

- Projet ou mission et demande d'origine ; workflow sélectionné, objectif et résultat attendu.
- Problème, utilisateur et acheteur présumés.
- Solution envisagée et alternatives déjà connues.
- Pays, segment, langue et périmètre de l'étude.
- Contraintes de temps, budget, compétences et accès : valeurs fournies ou inconnues.
- Décisions explicites du dirigeant, informations fournies et hypothèses séparées.
- Questions ouvertes et conséquence de chaque réponse manquante.

## plan.md

- Objectif et critères de fin de la mission ; équipes et responsables concernés.
- Mode : sous-agents réels ou analyses séquentielles.
- Limites : concurrence, tours de débat, temps et coût si mesurables.

| ID et tâche | Responsable unique | Entrées, versions et dépendances | Livrable | Critères et responsable d'acceptation | Priorité justifiée | Statut |
|---|---|---|---|---|---|---|

Les critères sont adaptés au workflow. Une production de contenus demande une revue éditoriale ; un développement demande des vérifications dans le dépôt ; un bilan financier demande des calculs contrôlables. Ne pas traiter tous les livrables comme des études.

## Contrat de tâche déléguée

- Identifiant unique dans la mission, par exemple T-001 ; objectif et périmètre exclu si utile.
- Responsable du résultat ; responsable d'acceptation, distinct de l'auteur si nécessaire et possible.
- Entrées : documents, versions ou dates et dépendances ; hypothèses lorsqu'une entrée manque.
- Livrable : chemin distinct et format attendu ; aucun autre agent n'écrit dans ce fichier pendant la tâche.
- Critères C-01, C-02, etc. : résultat observable et caractère indispensable ou secondaire.
- Outils, actions autorisées et limites connues ; questions qui bloquent réellement le travail.
- Fin : résultat, vérifications et restitution concise des limites et dépendances.

Le contrat peut être une section du plan ou le mandat transmis à l'agent. Ne pas le recopier dans plusieurs fichiers.

## livrables/<equipe>/<tache>-<document>.md

- Mission, auteur, destinataire et date ou version.
- Pour un document de référence, état documentaire : brouillon, en revue, référence, remplacé ou archivé. Consigner séparément l'acceptation de la tâche et les éventuelles corrections demandées.
- Contenu demandé : campagne, article, proposition, spécification, plan de test, bilan ou autre résultat du workflow.
- Références, faits, hypothèses et limites nécessaires à son usage.
- Vérifications réellement effectuées et points à traiter.
- Transmission : prochain responsable, dépendances et critères d'utilisation.

Pour le code et les assets, conserver les fichiers dans leur emplacement de travail approprié et ajouter des liens, sans les recopier artificiellement en Markdown. Pour une action extérieure, suivre séparément son état préparé, autorisé, exécuté et vérifié ; ne jamais déduire l'un de l'autre.

La validation porte sur la version remise. Conserver un relevé adapté au travail :

| Critère | Indispensable ? | Résultat : satisfait, non satisfait ou non vérifié | Preuve ou observation | Vérificateur et date |
|---|---|---|---|---|

Un critère indispensable non satisfait ou non vérifié laisse la tâche incomplète. Un document partiel ne devient pas un résultat accepté. Après correction, vérifier de nouveau les critères affectés de la nouvelle version.

## analyses/<tache>-<role>.md

- Rôle, tâche, date et périmètre.
- Questions examinées et méthode.
- Conclusions initiales.

| Affirmation | Nature | Preuve ou calcul | Limites |
|---|---|---|---|

Natures : fait externe sourcé ; information utilisateur ; estimation ; hypothèse. Pour un fait externe, fournir le lien, l'éditeur et la date de consultation. Pour une estimation, fournir la formule, les entrées et leur origine. Ne pas donner un pourcentage de confiance sans méthode.

- Risques, inconnues et informations inaccessibles.
- Questions ou objections à transmettre.
- Recommandation et conditions qui la feraient changer.
- Révision après échanges : corrections, justification et désaccords maintenus, en conservant la conclusion initiale.

## sources.md

| ID | Titre et éditeur | URL | Publication ou mise à jour connue | Date de consultation | Fait soutenu | Pays ou segment | Limites |
|---|---|---|---|---|---|---|---|

Un lien inaccessible n'est pas une source consultée. Garder les liens directs dans les analyses, même si des identifiants sont ajoutés dans le registre. Mentionner les éventuelles sources secondaires qui reprennent une origine commune.

## echanges.md

Utiliser le format de message défini dans [collaboration.md](collaboration.md). Après le débat, ajouter les sujets résolus, les corrections intégrées et les désaccords maintenus. N'enregistrer que des échanges réels ou des revues séquentielles clairement signalées.

## decisions.md

| ID | Date | Type | Auteur | Proposition ou décision | Motif et preuves | Objections ouvertes | Condition de réexamen |
|---|---|---|---|---|---|---|---|

Types : recommandation d'agent, choix de méthode du coordinateur, décision explicite du dirigeant. Ne pas convertir une recommandation en décision approuvée.

## etat.md

- Projet et dernière mise à jour.
- Workflow et phase courante : cadrage, analyse, production, revue, livraison ou suivi selon la mission.
- État : en cours, attente d'information, limite atteinte ou livrables remis. Pour l'étude, « dossier remis » reste utilisable.
- Mode d'exécution et limites applicables.
- Pour les tâches déléguées : profil, modèle/effort demandés, paramètres appliqués s'ils sont observables, identifiant réel de l'agent après lancement et nombre de tentatives. Ne pas convertir une requête préparée en exécution confirmée.
- Tâches terminées et liens vers les fichiers effectivement produits.
- Tâches en cours, responsables et dépendances.
- Questions ou obstacles nécessitant une réponse.
- Prochaines actions, par ordre de dépendance.
- Décision du dirigeant : en attente ou référence à une instruction explicite.

Pour les tâches, employer : à faire, en cours, à vérifier, terminée, bloquée ou annulée. Distinguer état d'une tâche et état de mission. Un échec d'outil décrit un événement et ne vaut pas réussite.

Conserver les versions des entrées et les résultats à réexaminer si elles changent. Un blocage indique cause et prochain responsable ou information nécessaire ; les travaux indépendants peuvent continuer.

Un livrable remis décrit la mission effectuée. Il ne prouve ni publication, ni déploiement, ni vente. Le « dossier remis » d'une étude ne signifie pas que le projet est lancé.

## Tableau de pilotage transversal

Le créer sous `entreprise/pilotage.md` seulement pour une mission de pilotage, avec le coordinateur comme rédacteur responsable.

| Objectif | Projet ou mission | Équipe et responsable | Indicateur et période | Résultat observé | Cible fournie ou proposée | Blocage | Prochaine action |
|---|---|---|---|---|---|---|---|

Chaque résultat possède une source ou un lien de livrable. Marquer indisponibles les mesures absentes ; séparer les cibles proposées de celles décidées par le dirigeant. Des bilans datés permettent de suivre l'évolution sans écraser les décisions passées.

## Bilan de fonctionnement

Pour une mission substantielle, ajouter au bilan existant : tâches terminées, bloquées ou annulées ; tâches acceptées à la première revue sur le nombre de tâches revues ; corrections ; temps et consommation réellement mesurés. L'absence de mesure ne signifie pas zéro.

Noter les retards ou reprises observés, leur cause étayée et les améliorations proposées. Comparer seulement des tâches de périmètre et contrôle comparables. Ce bilan n'autorise pas à modifier automatiquement le skill.

## Fiche de procédure

Pour documenter une méthode réutilisable propre à un produit ou service, préciser : nom et périmètre ; déclencheur ; responsable ; prérequis ; étapes ; contrôles et preuves ; exceptions ou blocages ; sortie et destinataire ; propriétaire documentaire et version. Référencer la méthode existante plutôt que la recopier.

Les étapes opérationnelles propres à un dépôt restent dans ce dépôt. La fiche décrit les opérations réellement prises en charge, pas des commandes supposées ou des automatisations non installées.

## Changement de périmètre

À consigner dans les décisions ou le suivi existant :

- Identifiant, origine, date connue et demande exacte.
- Version ou décision actuelle ; motif du changement.
- Tâches et documents affectés ; conséquences sur critères, effort, délai, coût et engagements, avec inconnues explicites.
- Traitement : précision compatible, instruction explicite intégrée ou proposition à arbitrer ; référence du mandat applicable.
- Mise à jour effectuée, résultats à réexaminer et prochaines actions.

## Transmission d'un livrable

- Mission, tâche, émetteur et destinataire.
- Lien et version du résultat, état de ses critères, preuves et limites utiles.
- Usage attendu, dépendances et action demandée au destinataire.
- Réception : confirmée en interne, réserves ou non confirmée ; référence de la réponse lorsqu'elle existe.
- Pour une action extérieure : mandat applicable, exécution réellement effectuée et vérification disponible, conservés séparément.

Une transmission simple peut tenir dans le compte rendu ou le message réel ; ne pas créer un document supplémentaire uniquement pour répéter un lien.

## Fiche d'incident

- Identifiant, signalement, responsable, périmètre et impact observé.
- Symptômes, preuves et chronologie ; heures précises seulement lorsqu'elles sont connues.
- Hypothèses, investigations et cause établie ou inconnue.
- Mesures proposées et effectuées, mandat applicable, résultats et effets à vérifier.
- État : ouvert, en traitement ou résolu après vérification ; obstacles et destinataires à informer dans le mandat.
- Prévention, tâches liées, propriétaires et documentation affectée.

Utiliser un document séparé pour un incident substantiel ; une anomalie locale peut rester dans son suivi existant. Appliquer [le processus d'incident](processus-transverses.md).

## Index documentaire

| Document et lien | Périmètre | Propriétaire | Version et date | État documentaire | Source ou décision liée | Remplace ou remplacé par |
|---|---|---|---|---|---|---|

Créer cet index seulement si le nombre de documents de référence le justifie. États : brouillon, en revue, référence, remplacé ou archivé. Séparer ces états des statuts des tâches et des autorisations d'action. Appliquer [la gestion documentaire](gestion-documentaire.md).

## Clôture de mission

Dans l'état ou le bilan existant : objectif ; résultats acceptés et liens ; état final réel de la mission ; tâches et critères incomplets ; décisions ; limites ; suites avec responsables ; contexte de reprise ; améliorations étayées proposées.

Un résultat partiel remis n'est pas une mission pleinement accomplie. La clôture d'une étude n'accepte pas automatiquement les projets de réalisation qu'elle recommande.

## dossier.md

1. Recommandation : poursuivre, modifier, tester davantage ou abandonner ; raisons et conditions.
2. Problème, cible, acheteur et proposition de valeur.
3. Marché : preuves, périmètre, éventuelle estimation et limites.
4. Alternatives et concurrence : comparaison avec sources.
5. Première version : parcours central, périmètre inclus et exclusions.
6. Faisabilité : options, dépendances et fourchettes d'effort.
7. Économie : modèle de revenus, coûts et scénarios calculables.
8. Risques, objections non résolues et faits encore non vérifiés.
9. Prochain test : hypothèse, cible, protocole, mesure, seuil proposé, effort et effet sur la décision.
10. Sources et liens vers les analyses.

Adapter la longueur à la mission. Si une section ne peut pas être renseignée, expliquer pourquoi et comment cela limite la recommandation.
