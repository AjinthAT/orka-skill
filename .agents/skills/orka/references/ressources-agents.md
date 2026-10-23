# Ressources IA : agents, modèles, effort et tokens

Le service RH d'Orka gère par défaut les ressources des agents IA. Le DRH conseille l'allocation, le rôle `recrutement-formation` qualifie les agents et prompts, le coordinateur applique les choix et lance les tâches, et le DAF examine les coûts. Une petite mission peut regrouper ces responsabilités dans l'agent principal ; ne pas lancer un agent de gestion pour chaque agent exécutant.

## Préparer l'allocation

Pour chaque tâche, retenir un résultat vérifiable, un rôle utile, le contexte minimal, un profil et un effort adaptés. Les profils [Codex](modeles-effort.md) et [Claude](modeles-effort-claude.md) restent des points de départ ; respecter les choix explicites et vérifier les capacités réelles de l'hôte avant lancement.

| Travail réel | Choix de départ à examiner | Vérification nécessaire |
|---|---|---|
| Extraire des faits d'une source connue, classer ou reformater | Profil exécution, effort compatible modéré | Exhaustivité, exactitude et format |
| Chercher, comparer et synthétiser des sources | Profil analyse | Sources effectivement lues, contradictions et inconnues |
| Concevoir ou construire avec des dépendances et risques concrets | Profil réalisation ; effort ajusté à la difficulté | Critères fonctionnels et résultats des vérifications |
| Contester une décision ou contrôler un résultat important | Profil revue, auteur distinct lorsque possible | Défauts étayés, pas simple accord avec la conclusion |
| Problème restant difficile après correction du brief et des accès | Expertise si disponible et justifiée | Nouvelle information ou gain utile, dans les limites de mission |

Le titre du rôle ne fixe pas un modèle permanent. Un analyste peut utiliser un profil léger pour extraire un tableau puis un profil plus exigeant pour interpréter un désaccord. Ne pas accroître l'effort pour compenser une source absente. L'effort de raisonnement, la longueur de réponse, la fenêtre de contexte et le plafond de tokens sont distincts ; aucun ne garantit à lui seul un coût ou une qualité.

Les préparateurs Codex et Claude acceptent les champs `profil`, `modele` et `effort` du mandat, ainsi qu'un fichier de capacités déclarées. Ces champs préparent des paramètres demandés ; ils ne configurent pas les comptes ni un moteur universel. Leurs champs autorisés restent ceux de [son guide](prompting-agents.md) : le budget et la consommation ci-dessous sont un suivi documentaire, pas de nouveaux paramètres de lancement.

## Plan puis consommation constatée

Conserver ces deux tableaux dans le plan ou l'état existant seulement si le suivi est utile. Sans identifiant réel, la tentative reste préparée.

| Tâche / tentative | Rôle / profil | Modèle et effort demandés | Motif du choix | Contexte utile | Limites fournies / applicables |
|---|---|---|---|---|---|

| Agent réel / période | Source et périmètre de mesure | Réglages appliqués ou inconnus | Tokens entrée / sortie / total | Sous-comptes éventuels | Coût constaté ou estimé | Résultat accepté / reprise |
|---|---|---|---|---|---|---|

- Relever les compteurs réellement exposés par l'hôte, en identifiant appel, tour, agent, tentative et période. Sans télémétrie, inscrire **indisponible**, jamais zéro ou une estimation issue de la longueur de réponse. Les pourcentages de quota d'un compte ne ventilent pas la consommation par agent.
- Suivre coordinateur, spécialistes et reprises sans compter deux fois le même appel. Ne pas additionner des instantanés cumulatifs ni un total parent incluant déjà les enfants avec leurs mêmes sous-totaux. Préciser la couverture quand elle est incomplète.
- Respecter le schéma du fournisseur. Dans l'Agents API OpenAI, cache en entrée et raisonnement en sortie sont déjà inclus dans les comptes parents ; les ajouter au total les compterait deux fois. Ne pas supposer le même schéma partout.
- Distinguer facture, coût calculé et hypothèse. Un calcul monétaire exige modèle réellement facturé, catégories, tarifs datés et autres frais applicables. Une consommation best-effort n'est pas une facture ni la mesure des limites d'un abonnement.

## Réduire le gaspillage sans dégrader le résultat

Réutiliser les sources et livrables valides, fournir les seules entrées utiles, éviter les doublons entre agents, regrouper les corrections et demander une restitution concise avec preuves. Réserver le modèle plus exigeant aux parties qui le justifient. Choisir entre travail direct et délégation selon le coût de coordination et les tâches indépendantes, pas selon le nombre de postes disponibles.

Comparer les variantes sur des critères identiques : acceptation initiale, erreurs constatées, reprises, durée et consommation disponibles. Un agent moins coûteux mais constamment repris peut dégrader le coût total. La [qualification](evaluation-agents.md) utilise des cas représentatifs et distingue autocontrôle, revue indépendante et mesures réelles.

Un plafond fourni par le dirigeant est suivi avec les moyens disponibles. À l'approche d'une limite observable, prioriser, réduire les travaux facultatifs ou rendre l'état partiel selon le mandat ; ne pas inventer un arrêt automatique. Sans compteur ou mécanisme d'application, signaler la limite de contrôle. Le registre SQLite actuel ne mesure ni ne plafonne les tokens.

Pour un relevé réutilisable, le [bilan local des agents](bilan-agents.md) calcule les acceptations initiales, reprises, tokens connus et coûts séparés par nature et devise. Le coordinateur fournit les tentatives et mesures avec leur provenance ; aucune extraction automatique du registre ou de l'hôte n'est fournie. Utiliser le détail et les dénominateurs plutôt qu'un classement global des agents sur des tâches incomparables.

## Sources et portée

[OpenAI — Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) décrit les réglages par agent et le coût de délégation ; [Agents API — Observability and usage](https://developers.openai.com/api/docs/guides/agents-api/observability) décrit ses propres compteurs. Sources consultées le 22 octobre 2026. Leur présence ne garantit pas que la session expose ces réglages ou cette télémétrie. Cette référence définit une procédure ; elle n'ajoute aucun collecteur, plafond technique ou tarif au logiciel local.
