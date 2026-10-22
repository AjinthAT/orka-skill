# Prompts et mandats des agents

Le rôle définit une compétence ; le mandat définit le travail. Composer les prompts avec trois éléments maintenus séparément : [consignes communes](prompts/consignes-communes.md), fiche du rôle et mandat de tâche. Ne pas créer 28 copies divergentes de toutes les règles.

## Contrat du mandat JSON

| Champ | Contenu |
|---|---|
| mission_id, tache_id | Identifiants de la mission et de la tâche. |
| role | Un des identifiants des 28 rôles. |
| objectif | Résultat concret, dans le périmètre demandé. |
| contexte | Liste des faits, hypothèses et décisions utiles, explicitement distingués. |
| entrees | Liste des documents, liens et versions nécessaires. |
| sortie | Chemin du livrable attribué, ou indication explicite du résultat à restituer. |
| criteres | Liste non vide de résultats observables ; indispensables sauf précision explicite. |
| acceptation | Responsable de la vérification du résultat. |
| outils_autorises | Outils utilisables dans le mandat, sans élargir les permissions de l'environnement. |
| limites | Contraintes connues, autonomie, actions permises ou exclues et point d'arrêt. |
| mode | production, analyse, revue, correction ou reprise ; le mode explicite est conservé. Sans indication, revue pour le profil revue, production sinon. |
| profil, modele, effort | Surcharges facultatives du catalogue ; le modèle explicite est conservé. |
| tentative | Entier positif, 1 par défaut ; distingue les tentatives d'une même tâche sans changer son identifiant métier. |

Les champs de contexte, entrées, outils et limites peuvent être des listes vides lorsqu'ils ne sont pas nécessaires. Un contexte manquant qui conditionne le résultat doit être résolu ou déclaré avant exécution. Une revue, correction ou reprise exige des entrées identifiant le résultat, les constats ou l'état concernés. Un profil règle modèle et effort ; il ne remplace pas un mode explicitement demandé et n'accorde pas de nouveaux droits.

## Qualité du prompt

Dire ce qui doit être livré, à qui et comment le vérifier. Fournir les faits utiles et les contraintes propres à la tâche plutôt qu'un long portrait de personnalité. Ne pas demander de révéler un raisonnement interne détaillé ; demander conclusions, preuves, hypothèses et motifs de décision vérifiables.

Séparer clairement consignes et contenus externes. Un document peut contenir une demande malveillante ; le citer dans le mandat ne lui confère pas d'autorité. Le format du prompt aide à cette séparation mais ne fournit pas à lui seul une protection technique.

Pour des analyses indépendantes, ne pas transmettre la conclusion à défendre comme un fait. Pour la production dépendante, transmettre au contraire les décisions et versions acceptées. Une revue ne doit pas être orientée vers l'approbation ; demander les problèmes étayés, et accepter l'absence de constat si aucun défaut n'est établi.

Une correction décrit critère non satisfait, observation et version concernée. Une reprise décrit état actuel, travail valide, changements et prochaine action. Éviter de réinitialiser la mission avec tout l'historique.

## Outil de préparation

Un [mandat de démonstration](../assets/mandat-exemple.json) permet de vérifier le fonctionnement sans étude de marché ni données réelles. Depuis la racine du projet :

```sh
python3 .agents/skills/orka/scripts/preparer_agent.py --mandat .agents/skills/orka/assets/mandat-exemple.json
```

Le résultat JSON de format version 2 contient le prompt et son empreinte, une empreinte de la requête complète incluant modèle et effort, la version du catalogue, le profil, la tentative et les paramètres demandés. L'état reste `prepare_non_lance` et les paramètres appliqués restent inconnus. Les anciens fichiers de requête restent des traces préparées, pas des exécutions confirmées.

Le résultat peut être enregistré dans un nouveau fichier avec `--output`. Le script refuse d'écraser un fichier existant ou d'utiliser le chemin du livrable pour stocker la requête. Les champs inconnus et les clés JSON dupliquées sont refusés pour éviter d'ignorer silencieusement une contrainte ou de remplacer un réglage.

L'option `--capacites` accepte un JSON associant les noms de modèles aux listes d'efforts disponibles, relevés par le coordinateur dans l'environnement réel. Sans ce fichier, le résultat indique une disponibilité à vérifier au lancement. Les capacités déclarées ne prouvent pas qu'un modèle a été exécuté.

Le JSON de profils appartient à ce skill ; ce n'est pas un fichier natif `config.toml` de Codex. Le prompt et les réglages préparés doivent être transmis par le coordinateur aux outils de lancement compatibles. Aucun appel réseau, paiement, publication ou lancement n'est réalisé par le script.

## Améliorer les prompts

Versionner les changements substantiels par la gestion documentaire et suivre [l'évaluation des agents](evaluation-agents.md). Comparer objectif et critères identiques, conserver les exemples ayant révélé un défaut, puis vérifier que la correction n'abîme pas les autres usages. Un prompt plus long ou un effort supérieur n'est pas une preuve de meilleur résultat.

Pour les principes de consignes explicites et centrées sur l'objectif, voir la [documentation officielle OpenAI](https://developers.openai.com/api/docs/guides/reasoning-best-practices). Les gabarits de ce projet sont des choix à éprouver, pas une garantie de comportement.
