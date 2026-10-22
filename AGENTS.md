# Instructions du projet Atelier Agents

Ce dossier définit une équipe d'agents et ses workflows. Il contient les instructions Markdown, un catalogue JSON de profils, un préparateur de mandats et un registre de supervision local persistant. Ces outils ne lancent aucun modèle ni agent.

- Pour une mission confiée à l'équipe de l'entreprise, lire [.agents/skills/atelier-agents/SKILL.md](.agents/skills/atelier-agents/SKILL.md), puis uniquement les références utiles à la mission.
- Pour modifier le système lui-même, travailler sur les instructions et leur cohérence ; ne pas lancer une étude commerciale automatiquement.
- Conserver la distinction entre procédures documentées, agents réellement exécutés et fonctionnalités futures.
- Les missions d'un produit vont dans `projets/<identifiant>/` ; les missions transversales dans `entreprise/missions/<identifiant>/`. Ne pas mélanger leurs preuves et décisions. Le code reste dans le dépôt de développement désigné.
- Ne pas modifier les livrables d'un autre agent en cours de travail. Le coordinateur est responsable des fichiers partagés.
- Adapter le processus à la mission et accepter les tâches sur leurs critères vérifiés. Utiliser une sortie distincte par tâche ; avant de remplacer un rédacteur, obtenir son arrêt ou sa fin. Les changements d'entrées entraînent le réexamen des résultats concernés.
- Pour les changements, transmissions et incidents, utiliser les processus communs du skill. Pour les documents de référence, identifier propriétaire, version et provenance ; distinguer état documentaire, avancement et autorisation d'action.
- Le coordinateur gère les agents, leur contexte et les profils modèle/effort. Les paramètres demandés ne sont pas des paramètres effectivement appliqués. Pour préparer les requêtes de manière répétable, utiliser l'outil du skill ; ne pas modifier la configuration personnelle pour appliquer un choix de mission.
- Si un registre de supervision est utilisé, réserver avant lancement, rattacher l'identifiant réel puis conserver la réservation jusqu'à confirmation de fin du rédacteur. Ne pas libérer une tâche sur la seule base d'un délai dépassé. Les contrôles du registre ne protègent pas les opérations qui le contournent.
- Respecter les autorisations de la session. Une fiche de rôle ne donne aucun droit supplémentaire sur un service ou une action externe.
- Si un index `.codegraph/` existe à la racine, consulter CodeGraph avant les recherches de compréhension du code. Sinon, ne pas créer d'index sans demande.
- Pour une future implémentation impliquant une bibliothèque, un SDK ou un service cloud, consulter sa documentation actuelle via Context7 : résoudre l'identifiant, puis interroger un concept précis. Pour OpenAI, compléter avec la documentation officielle.
