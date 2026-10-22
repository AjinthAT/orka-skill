# Atelier Agents

Une entreprise composée d'agents spécialisés pour étudier, concevoir, développer, commercialiser et suivre des produits et services, selon les missions confiées par le dirigeant.

## Ce qui est disponible

Un skill de coordination, 28 rôles répartis en 8 équipes, 9 workflows d'entreprise, les procédures communes et des modèles de documents. Un outil local prépare les prompts et paramètres à partir d'un catalogue de profils. Aucun serveur, agent permanent ou déclenchement automatique n'est installé ; l'outil de préparation n'effectue aucun appel de modèle.

Un [superviseur local persistant](.agents/skills/atelier-agents/references/supervision-locale.md) enregistre maintenant tâches, dépendances, réservations et événements dans une base locale. Il contrôle la capacité commune du registre, les tentatives et l'acceptation des fichiers soumis. Le coordinateur reste responsable du lancement et du constat de fin des agents ; le registre n'exécute aucun modèle.

Le skill est le manuel de travail. L'agent coordinateur exécute ce manuel avec les outils disponibles dans la session. Les fiches de rôles deviennent des instructions pour les spécialistes effectivement lancés ; leur présence sur disque ne crée pas des agents.

## Responsable des agents, modèles et prompts

Le coordinateur est aussi le responsable des agents : il choisit les spécialistes, prépare leurs mandats, réserve les places, suit leurs résultats et organise les corrections. Les [six profils d'exécution](.agents/skills/atelier-agents/references/modeles-effort.md) proposent un modèle et un effort selon la tâche, avec des règles d'escalade et de disponibilité.

Le [prompting](.agents/skills/atelier-agents/references/prompting-agents.md) assemble les règles communes, la fiche du rôle et les critères de la tâche. L'outil [preparer_agent.py](.agents/skills/atelier-agents/scripts/preparer_agent.py) produit une requête JSON prête à être vérifiée puis transmise par le coordinateur à un outil compatible. Il conserve les choix explicites et ne remplace pas silencieusement un modèle indisponible. Une requête préparée reste distincte d'un agent lancé.

## Efficacité et qualité du travail

Le niveau d'organisation s'adapte à la mission : suivi compact pour un petit livrable, coordination pour les tâches liées, débat pour une décision incertaine à fort impact. Chaque tâche a un responsable, une sortie distincte et des critères d'acceptation vérifiables.

Les travaux indépendants peuvent avancer en parallèle dans la capacité disponible. Les dépendances bloquantes passent en priorité ; une entrée modifiée fait réexaminer les seuls résultats affectés. Les corrections sont ciblées et les échanges utiles sont regroupés. Les bilans relèvent les reprises et mesures réellement disponibles pour évaluer l'efficacité, sans annoncer de gain non mesuré.

## Les équipes

| Équipe | Responsabilités |
|---|---|
| Direction et stratégie | Coordination, marché, concurrence et évaluation critique. |
| Marketing et communication | Stratégie, rédaction, SEO, réseaux sociaux et acquisition. |
| Commercial | Vente, prospection et partenariats. |
| Produit et design | Priorités, gestion de projet, parcours et interfaces. |
| Technique | CTO, architecture, frontend, backend, sécurité, QA et DevOps. |
| Finance et administration | Budget, rentabilité, pièces et échéances. |
| RH | DRH, recrutement, intégration et formation. |
| Relation client | Support, adoption et fidélisation. |

Chaque rôle possède une mission, des entrées, des livrables, des interlocuteurs et des critères de contrôle dans les [fiches d'équipe](.agents/skills/atelier-agents/references/roles.md). L'ensemble est disponible sans exiger 28 agents actifs en même temps.

## Confier une mission

Demander au skill `atelier-agents` de mobiliser les équipes utiles, avec sous-agents si souhaité et disponibles. Préciser le résultat attendu et les contraintes déjà connues. Il peut préparer une stratégie marketing, produire les contenus demandés, organiser un développement autorisé, examiner des retours clients ou préparer un bilan de gestion.

Pour le premier projet, une étude constitue un point de départ :

Ouvrir ce dossier dans Codex et demander :

> Utilise le skill atelier-agents pour étudier le projet suivant : [mon idée]. Fais travailler des sous-agents spécialisés, organise leurs objections et produis un dossier de décision dans ce projet. Marché visé : [pays ou segment]. Contraintes connues : [temps, budget, équipe].

Les éléments entre crochets sont à remplacer. Si le skill n'apparaît pas encore dans la session, ouvrir un nouveau chat dans ce dossier ou demander explicitement de lire [.agents/skills/atelier-agents/SKILL.md](.agents/skills/atelier-agents/SKILL.md). La disponibilité des outils de sous-agents dépend de l'environnement.

Si la délégation n'est pas disponible ou autorisée, le coordinateur peut appliquer successivement les points de vue. Il doit alors annoncer une analyse séquentielle, sans la présenter comme le débat de plusieurs agents indépendants.

## Parcours

Idée → étude et décision → produit et conception → réalisation et qualité → lancement et vente → support et amélioration.

Marketing, finance, RH et pilotage interviennent sur les phases qui nécessitent leur travail. Une mission ciblée peut commencer directement dans le service concerné ; elle n'impose pas de recommencer tout ce parcours. Les [workflows](.agents/skills/atelier-agents/references/workflows-entreprise.md) précisent les dépendances et les transmissions.

L'étude peut recommander un test terrain. Un agent ne doit pas annoncer des entretiens clients, des ventes ou une validation de la demande sans résultats réels.

## Documents

| Document | Utilité |
|---|---|
| [Skill](.agents/skills/atelier-agents/SKILL.md) | Point d'entrée exécutable par un agent. |
| [Rôles](.agents/skills/atelier-agents/references/roles.md) | Organisation, 28 rôles et fiches des 8 équipes. |
| [Gestion des agents](.agents/skills/atelier-agents/references/orchestration-agents.md) | Allocation, lancement, suivi, contexte et reprise des spécialistes. |
| [Supervision locale](.agents/skills/atelier-agents/references/supervision-locale.md) | Registre persistant, dépendances, réservations, alertes à la demande et acceptation. |
| [Modèles et effort](.agents/skills/atelier-agents/references/modeles-effort.md) | Profils proposés, choix explicites, compatibilité et escalade. |
| [Prompting](.agents/skills/atelier-agents/references/prompting-agents.md) | Construction des mandats et utilisation de l'outil local. |
| [Workflows d'entreprise](.agents/skills/atelier-agents/references/workflows-entreprise.md) | Marketing, vente, réalisation, lancement, clients, finance, RH et pilotage. |
| [Workflow d'étude](.agents/skills/atelier-agents/references/workflow-etude.md) | Étapes, dépendances et critères de sortie. |
| [Collaboration](.agents/skills/atelier-agents/references/collaboration.md) | Missions, échanges, débats, limites et reprise. |
| [Pilotage des missions](.agents/skills/atelier-agents/references/pilotage-missions.md) | Niveau d'effort, tâches prêtes, acceptation, corrections et mesures. |
| [Processus communs](.agents/skills/atelier-agents/references/processus-transverses.md) | Demandes, changements, transmissions, incidents et clôture entre les workflows métiers. |
| [Gestion documentaire](.agents/skills/atelier-agents/references/gestion-documentaire.md) | Propriétaires, versions de référence, mises à jour et archivage. |
| [Modèles](.agents/skills/atelier-agents/references/modeles.md) | Structure des dossiers, sources, décisions et état. |
| [Validation](.agents/skills/atelier-agents/references/validation.md) | Scénarios pour vérifier le comportement du skill. |
| [Évaluation et évolutions](.agents/skills/atelier-agents/references/evaluation-agents.md) | Comparer prompts et profils, préserver une référence et prioriser les renforcements suivants. |
| [Implémentation](docs/IMPLEMENTATION.md) | Fonctionnement dans Codex et évolution vers une application autonome. |

Les résultats d'une mission produit seront enregistrés sous `projets/<identifiant>/` ; ceux d'une mission transversale sous `entreprise/missions/<identifiant>/`. Le code reste dans le dépôt désigné. Aucun projet commercial ni résultat d'activité n'a encore été renseigné.

Les procédures distinguent les états des tâches, ceux des documents et les autorisations d'action. Une tâche terminée, un document de référence et une publication autorisée ne sont pas interchangeables. Les modèles de changement, transmission, incident et clôture sont créés seulement lorsque la mission les nécessite.

## Références techniques

Structure du skill et découverte locale : [documentation officielle OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills). Séparation entre instructions et outils : [documentation officielle OpenAI — Build skills for plugins](https://developers.openai.com/plugins/build/skills).

Ces références documentent le format des skills. L'organisation de l'entreprise et le protocole de débat sont les choix proposés par ce projet.
