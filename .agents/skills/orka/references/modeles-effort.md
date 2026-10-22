# Choisir modèle et effort

Ces réglages constituent le profil Codex fourni avec Orka, pas un catalogue universel. Pour Claude ou un autre assistant, conserver les critères de choix et utiliser les modèles et réglages natifs disponibles. Sans catalogue local compatible, préparer les mandats directement et utiliser le suivi documentaire ; le préparateur JSON et le registre qui l'appelle restent facultatifs et spécifiques au catalogue fourni.

Les profils sont des choix de départ du projet, à évaluer sur les tâches réelles. Ils ne garantissent ni qualité ni économie. Les modèles et efforts ci-dessous étaient exposés dans l’environnement de développement de référence le 22 octobre 2026 ; leur disponibilité doit être vérifiée au lancement suivant. Le catalogue ne contient aucun tarif ni budget inventé.

## Profils proposés

| Profil | Modèle demandé | Effort | Usage |
|---|---|---|---|
| coordination | gpt-6.1-sol | high | Décomposition, dépendances et synthèse entre équipes. |
| execution | gpt-6-luna | medium | Contenu ou traitement simple avec brief et faits établis. |
| analyse | gpt-6.1-sol | medium | Recherche, stratégie, produit, économie ou synthèse nécessitant du jugement. |
| realisation | gpt-6.1-sol | high | Développement, architecture et exploitation dans le mandat. |
| revue | gpt-6.1-sol | high | Vérification critique, qualité et sécurité. |
| expertise | gpt-6-astra | high | Problème particulièrement ambigu ou échec de raisonnement constaté après correction du contexte. |

Les réglages de référence et les rôles par défaut sont dans [profils-modeles.json](profils-modeles.json). Un même rôle peut demander un autre profil pour une tâche différente. Le titre du poste ne suffit pas à déterminer l'effort.

## Décider avant le lancement

1. Respecter un modèle ou effort explicitement demandé par le dirigeant, s'il est disponible et compatible. Ne pas le remplacer par un modèle plus récent de sa propre initiative.
2. Sinon, partir du profil du rôle et examiner la tâche : ambiguïté, nombre de dépendances, besoin de vérification, conséquence d'une erreur et qualité du contexte.
3. Descendre vers l'exécution pour un traitement borné de faits établis ; préférer analyse, réalisation ou revue pour le jugement nécessaire. Réserver expertise aux cas qui le justifient avec un motif enregistré.
4. Vérifier le couple modèle/effort dans les capacités réellement fournies par l'environnement. Un niveau d'effort supporté par un modèle ne l'est pas nécessairement par un autre.
5. Enregistrer les paramètres demandés. Les paramètres effectivement utilisés restent inconnus tant qu'aucune information du moteur ne les confirme.

L'effort de raisonnement, la longueur de réponse, le temps disponible et le budget sont des réglages distincts. Ne pas choisir automatiquement `max` ou `ultra` ; les niveaux plus élevés doivent répondre à un besoin observé et tenir dans les limites de mission.

## Escalade et repli

Avant de monter en gamme, vérifier la cause du défaut : brief incomplet, source absente, critère contradictoire ou manque d'accès. Une hausse d'effort ne crée pas des faits ou une permission.

Pour un échec de raisonnement identifiable, proposer un effort compatible supérieur ou le profil expertise, avec les mêmes critères et les éléments du défaut. Respecter les limites de tentatives ; l'escalade ne réinitialise pas le budget. En cas d'indisponibilité, ne pas substituer silencieusement un autre modèle. Conserver la demande explicite ; employer un repli seulement s'il est compatible avec les consignes et le budget, en le signalant, sinon indiquer le blocage.

Le script de préparation refuse un couple absent du catalogue ou des capacités fournies. Il ne choisit pas de repli automatique. Pour un nouveau modèle, vérifier sa documentation et les outils avant de mettre le catalogue à jour.

## Sources et limites

OpenAI documente les réglages par agent et les règles d'héritage dans [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Le choix selon le travail et les compromis est abordé dans [Model selection](https://developers.openai.com/api/docs/guides/model-selection). Les profils et seuils d'escalade ci-dessus sont notre politique proposée, pas des performances certifiées par ces sources.

Un catalogue de paramètres demandés ne prouve pas le modèle effectivement utilisé par une exécution. Le skill ne modifie pas la configuration personnelle et ne dépend pas de fichiers natifs d'agents persistants.
