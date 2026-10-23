# Sonde modèle L4 — décision de non-lancement

Propriétaire : coordinateur de maintenance. Version : 1. Date : 23 octobre 2026. État : **contrôle terminé ; sonde non lancée**. Provenance : demande du dirigeant autorisant une seule sonde sur les données fictives, uniquement avec un contexte neuf et les trois seuls outils préparés, sans modification des réglages personnels. Cette décision est distincte d'un échec de modèle ou d'une observation L4.

## Décision

**Zéro sonde modèle lancée.** La condition d'exclusivité des outils ne peut pas être établie avec les interfaces exposées dans cette conversation avant lancement. La demande prévoit explicitement de ne rien lancer dans ce cas ; aucune relance ou tentative avec un simple engagement textuel n'a été faite.

Le [raccordement logiciel](../evals/raccordement-L4-2026-10-23/README.md) est testé, mais les deux connexions fictives sont toujours des gabarits inactifs. La copie locale du pont correspond à sa source actuelle. Aucun serveur n'a été enregistré ou activé dans Codex pour ce contrôle.

| Moyen inspecté, sans l'appeler | Contexte neuf | Exclusivité des trois outils avant lancement |
|---|---|---|
| `spawn_agent` avec `fork_turns="none"` | Option sans historique exposée | Même surface d'outils héritée ; aucun paramètre d'enregistrement du pont ou de remplacement du catalogue exposé |
| `create_thread` | Création avec un nouveau prompt possible | Aucun paramètre de catalogue exclusif ou de raccordement par conversation ; le prompt démarrerait sans cette preuve préalable |
| `fork_thread` | Historique conservé | Ne satisfait déjà pas la condition de contexte neuf |
| Gabarits MCP préparés | Ne créent pas une conversation | Décrivent les outils du serveur ; ne retirent pas le shell, les fichiers ou les autres outils natifs de l'hôte |

Les schémas des outils disponibles sont la preuve pour cette session. La [documentation officielle des sous-agents](https://learn.chatgpt.com/docs/agent-configuration/subagents) explique aussi l'héritage des permissions et des paramètres ; elle ne prouve pas une configuration appliquée à une future exécution. Cette décision ne conclut pas que tous les clients Codex ou tous les moteurs sont incapables de réaliser ce cloisonnement.

Un prompt disant « utilise seulement trois outils » n'aurait pas retiré les autres capacités. Le conteneur protège le processus de fichiers lorsqu'il est utilisé ; il ne force pas un modèle disposant du shell ou d'outils directs à passer par ce processus. Aucun agent n'a donc été créé pour découvrir après coup son catalogue.

## Préservation vérifiée

- Zéro contexte modèle, sous-agent, nouveau chat ou message à un chat créé pour la sonde ; zéro observation importée.
- Les treize fichiers du précédent instantané ciblé, comprenant les réglages personnels inspectés et les documents protégés, sont inchangés.
- Les douze dossiers de sorties de développement L4 sont vides ; aucun répertoire de résultats n'est présent dans la campagne figée.
- Aucun contenu réservé, grille privée, procédure opérateur globale, plan privé ou manifeste complet n'a été ouvert. Leur sceau intégral n'a pas été recalculé, car cela nécessiterait leur lecture.
- Aucun gabarit, réglage, authentification ou installation personnelle n'a été modifié. Les sondes logicielles antérieures restent conservées et ne deviennent pas des sondes modèle.

## Condition de reprise

Reprendre seulement quand un hôte permet de constater **avant le premier appel modèle** un contexte neuf et un catalogue effectif limité au pont `lister`, `lire`, `ecrire`, sans modifier les réglages personnels. Préserver la limite d'une sonde et les seules données fictives. Si un autre hôte ou un autre protocole est nécessaire, le décrire séparément ; ne pas modifier ni qualifier rétroactivement L4. Cette demande est traitée par sa branche de non-lancement, sans exécution en attente ou en arrière-plan.
