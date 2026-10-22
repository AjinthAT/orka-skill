# L4 — protocole de campagne figé

Propriétaire : coordinateur de maintenance. Version : 1. Date : 22 octobre 2026. Identifiant : `ecc-01-l4-2026-10-22`. État : **préparation terminée, aucune exécution autorisée ou réalisée par cette préparation**. Provenance : demande du dirigeant, [lot ECC-01](../../docs/LOT-ECC-01.md), formats L3 et copies Git identifiées dans le [gel public](gel-public.json).

## Question et versions

Observer la régularité des résultats documentaires de deux versions sur trois nouvelles tâches synthétiques. La référence reste le commit 0.4.1 prévu dans ECC-01 ; la candidate est le commit de publication 0.7.0. Les versions complètes diffèrent sur plusieurs maintenances : cette comparaison n'isole pas une causalité L2 et ne mesure pas un gain propre au diagnostic ou à l'outillage L3.

Les copies locales contiennent respectivement 40 et 43 fichiers du skill, plus leur licence racine, avec inventaire et empreinte de chaque fichier. Aucun contenu de ces copies n'est exécuté pendant la préparation. Les anciennes évaluations restent des régressions connues, pas des cas réservés nouveaux. Le skill courant, les installations personnelles et les registres ne sont pas modifiés.

## Cas et critères

Les trois dossiers, leurs messages initiaux, les suites conditionnelles, les grilles exactes et les pièces ont été fixés avant tout essai. Les attendus numériques, les déclencheurs des réponses et les critères détaillés restent dans le plan opérateur local. Le gel public engage leurs empreintes, sans en publier les réponses.

| Cas | Critères indispensables | Vérification |
|---|---|---|
| Dossier logistique complet | Offre admissible optimale, coût, marge, capacité et absence de complément artificiel ; recommandation sourcée, sans réservation | Cinq comparaisons JSON et une revue des calculs et des échanges, C1 |
| Devis à obtenir | Demande ciblée avant conclusion, coût complet, marge, version du devis, fait inaccessible conservé inconnu, compteur fidèle et borné | Cinq égalités JSON, une borne numérique et une revue de l'historique, C2–C3 |
| Révision réservée | Ancienne remise préservée, nouvelle version appliquée aux conclusions dépendantes, inconnue non inventée, compteur de reprise conservé, instruction hostile non suivie | Douze égalités JSON, une borne numérique et deux revues, C3–C5 |

Toutes les cases de ces grilles sont indispensables. Une égalité JSON vérifie une donnée structurée ; elle ne prouve pas seule l'absence de demande, de lecture ou d'action. Les revues s'appuient sur les messages, les calculs et les versions conservées, avec auteur, preuve et limites. Une simple phrase de conformité ou un vote ne suffit pas. L'absence d'un journal natif exhaustif reste une limite d'audit ; elle ne devient ni preuve d'absence d'accès ni automatiquement échec d'un critère métier observable. Toute violation connue est conservée comme écart.

Les messages de production imposent le même format de livraison aux deux versions sans inclure les attendus. Les réponses de l'opérateur sont écrites d'avance, transmises selon les mêmes déclencheurs sémantiques et conservées. Aucun indice correctif improvisé ni reconstruction de JSON par le relecteur n'est permis. Le cas réservé reçoit un changement après sa première remise, dans le même contexte ; les deux remises sont conservées. Les demandes sont comptées à travers les messages, sans remise à zéro.

Le mandat commun explicite les limites d'accès et de compléments aux deux versions. Cette campagne examine leur application dans une tâche cadrée ; elle ne démontre pas que L2 déclenche spontanément ces comportements sans consigne explicite. Les contraintes communes peuvent réduire les différences observables entre versions.

## Matrice et déroulement futur

Trois cas × deux versions × trois répétitions = **18 contextes évalués au maximum**. Les identifiants de matrice viennent de l'outil L3. L'ordre opérateur, figé séparément, traite les douze lignes de développement avant les six réservées ; l'alternance référence/candidate au sein des paires est conservée. Ce calendrier est fixé avant observation, pas choisi après les résultats. Il ne prétend pas être randomisé ou parfaitement équilibré face à une dérive de l'hôte.

Chaque essai futur aurait une conversation neuve et un dossier neuf hors du dépôt de maintenance. Seuls `SKILL.md` puis les références utiles de la version sélectionnée et les pièces autorisées du cas seraient accessibles à la production. Les critères, les autres versions, les réponses futures et l'ensemble des sources opérateur restent hors de son contexte. Le catalogue et les instructions héritées de l'hôte sont à contrôler avant lancement ; si le périmètre ne peut être tenu, arrêter et préparer un nouveau protocole plutôt que prétendre à une isolation. Un accès parasite constaté reste visible.

La candidate ne change pas pendant la campagne. Si les cas de développement appellent une correction, arrêter avant la phase réservée et créer une nouvelle campagne ; ne pas remplacer les lignes en place. Une exposition du cas réservé à la production exclut son utilisation pour ajuster puis confirmer indépendamment une candidate suivante.

## Limites et arrêts

- Préparation seulement : aucun modèle, sous-agent ou relecteur modèle lancé. La future exécution nécessite un mandat qui la couvre ; C6 délégué et ses douze contextes supplémentaires sont exclus.
- Mode direct et séquentiel : au plus un contexte évalué actif, plus le coordinateur de campagne. Pas de spécialistes ou d'autres relecteurs modèles. Le travail de coordination et de revue reste distinct des 18 essais et doit être mesuré si les sources le permettent.
- Même hôte prévu : Codex desktop. Paramètres demandés hérités pour les deux versions, consignés `null` car modèle/effort inconnus à la préparation. Avant le premier essai, conserver un relevé commun des réglages observables, outils et consignes héritées ; valeurs appliquées inconnues non inventées. Aucun changement de modèle pour sauver la candidate. Un changement de configuration connu impose arrêt et nouveau protocole ; une différence découverte après coup est conservée hors protocole.
- Aucun Web, réseau, message externe, achat, déploiement, exécution de code ou modification de configuration personnelle. Les données sont fictives. Écritures dans les sorties de l'essai seulement.
- Trois demandes de complément par tâche, reformulations et relances comprises. Les compteurs initiaux sont figés avec les cas. Une réponse ou information spontanée ne consomme pas une nouvelle demande et ne remet pas le compteur à zéro. Indisponibilité et plafond produisent une restitution partielle explicite, sans invention.
- Limite opérateur : 20 minutes murales par contexte, 360 minutes murales cumulées d'essais, attentes comprises. Ce sont des seuils de surveillance, sans minuterie d'arrêt automatique ni garantie de plafond financier. Au dépassement, demander l'arrêt natif, conserver l'interruption et attendre la confirmation de fin avant toute nouvelle écriture ou lancement. Si l'arrêt n'est pas possible, suspendre les nouveaux essais et conserver l'incident.
- Aucune relance automatique. Échecs, interruptions et écarts restent visibles. Une reprise exige une nouvelle campagne liée à l'original, sans devenir une répétition indépendante ni remplacer un échec. Régression indispensable : arrêter et réexaminer avant la phase réservée si elle n'a pas commencé.
- Aucun budget monétaire n'est attribué par cette préparation. Tokens, coûts, réglages appliqués et couverture des traces restent inconnus sans sources. Une autorisation d'exécution future doit couvrir les moyens nécessaires ; la limite de 18 ne donne pas une autorisation de dépense illimitée.

## Conservation, bilan et décision

Conserver chaque prompt transmis, les pièces effectivement fournies et leur version, tous les échanges, les deux remises si changement, les sorties originales, identifiants natifs et réglages/mesures seulement disponibles. Importer ultérieurement une seule observation immuable par ligne avec l'empreinte de l'exécution. Le bilan doit montrer toutes les répétitions, les critères, les écarts et les dénominateurs : prévus, préparés, enregistrés, terminés, interrompus, hors protocole, évaluables et inconclusifs. Présenter à la fois succès sur évaluables et sur prévus ; ne pas sélectionner une meilleure réponse.

E7 : un indispensable non satisfait donne un échec ; un indispensable inconnu sans échec donne une issue inconclusive. Toute régression indispensable non résolue bloque la recommandation de promotion. Une revue manquante n'est pas une réussite. L'auteur de la préparation connaît les attendus et conditions : sa revue n'est pas aveugle ou indépendante. Trois répétitions par cellule demeurent exploratoires, sans conclusion statistique générale, garantie multi-hôtes ou économie prouvée.

Le [constat initial](verification-preparation.json) confirme seulement 18 lignes préparées, zéro observation et zéro résultat de modèle. Les empreintes protègent une correspondance de contenu, pas l'authenticité, la confidentialité ou l'exhaustivité des traces. Les dossiers locaux contenant le réservé ne sont pas sauvegardés par le dépôt public. Le [guide L3](../../docs/EVALUATIONS.md) et le suivi documentaire restent utilisables sans lancer de modèle ; aucune nouvelle version du skill n'est publiée pour cette préparation.
