# Première évaluation comparative d'Orka

Propriétaire : coordinateur de maintenance. Version du protocole : 1. Date : 22 octobre 2026, Europe/Paris. Référence évaluée : Orka 0.4.0, commit `031a69c`. Tous les cas et chiffres métier sont **synthétiques**. Aucun dossier privé, client réel, service externe ou entretien n'est utilisé.

## Question et plan fixés avant les essais

Observer si les instructions et la délégation changent la conformité, les erreurs et les corrections nécessaires sur trois tâches. Comparer une exécution par cellule, soit neuf coordinateurs indépendants :

| Condition | Traitement |
|---|---|
| A — assistant seul | Demande et données du cas ; aucune lecture ni utilisation d'Orka, aucune délégation. |
| B — Orka sans délégation | Même demande et mêmes données ; copie figée du skill Orka 0.4.0, références chargées selon le besoin ; aucune délégation. |
| C — Orka avec spécialistes | Même demande et mêmes données ; même copie figée ; exactement deux spécialistes bornés, avec fichiers distincts, puis synthèse du coordinateur. |

La délégation de C est **imposée par le protocole**, même sur le petit cas. Elle ne représente pas le choix adaptatif normal d'Orka, qui pourrait traiter ce cas directement. Au plus un retour de correction par spécialiste. Les spécialistes ne délèguent pas. Le coordinateur dispose de deux places enfants ; la limite totale de quatre agents inclut le coordinateur de l'évaluation.

Chaque coordinateur est lancé avec `fork_turns=none`, sans historique de la conversation principale. Les réglages modèle/effort sont hérités de l'hôte, sans surcharge, pour les neuf coordinateurs et leurs spécialistes : ce pilote ne compare pas le catalogue de profils. Les paramètres réellement appliqués et compteurs sont notés inconnus si l'interface ne les fournit pas. La description des skills et les règles générales de l'hôte peuvent rester disponibles à tous ; l'absence absolue de connaissance préalable d'Orka n'est pas démontrable.

Les cellules sont exécutées successivement, hors sous-tâches internes de C. Ordre contrebalancé : cas 01 A/B/C ; cas 02 B/C/A ; cas 03 C/A/B. Il ne neutralise pas toutes les variations de disponibilité de l'hôte.

## Périmètre et conservation

Pour chaque cellule, une copie indépendante des seules entrées est placée hors du dépôt, dans un dossier temporaire distinct. Les agents n'ont pas l'autorisation de lire les autres cellules ni les rubriques. Les espaces de fichiers restent techniquement partagés : ce sont des consignes d'isolement, pas un environnement de sécurité séparé. Pas de Web, messages externes, compte ni dépense ; lecture/écriture des fichiers du cas et exécution locale du prototype seulement.

Conserver le prompt de lancement, les identifiants d'agents, leurs sorties finales, le livrable initial, la trace factuelle des vérifications et les corrections. Les variantes avec Orka lisent une copie du skill antérieure aux changements de documentation effectués en parallèle. Conserver les empreintes des entrées et du skill. Les grilles sont dans `criteres.json`, distinctes des données communiquées aux agents.

Le coordinateur de l'évaluation examine les sorties originales après leur fin, sans les corriger. Chaque critère reçoit `satisfait`, `non_satisfait` ou `non_verifie`, avec preuve. Une correction nécessaire est une action restante, pas un résultat qui aurait déjà été obtenu. Les corrections internes réellement effectuées par C sont conservées séparément des corrections après évaluation. Les tests du prototype sont lancés sur une copie après capture des sorties.

## Mesures et limites

Relever conformité par critère, défauts confirmés, corrections restantes, nombre réel d'agents et taille des sorties. Conserver heures d'envoi et de première observation de fin ; leur différence inclut la latence d'observation et ne constitue pas un temps de calcul moteur. Ne pas comparer ces durées comme une mesure de productivité sans répétitions et contrôle des facteurs de confusion. Les tokens/coûts restent indisponibles sans télémétrie : ni estimation depuis la longueur, ni ventilation depuis le quota du compte.

Trois cas, une exécution par condition, pas de relecteur aveugle indépendant et tâches sur documents fournis : ce pilote peut révéler des défauts, mais ne démontre ni supériorité générale, ni économie, ni validité commerciale, ni qualité de recherche Web. Ne pas modifier les consignes évaluées pour améliorer les résultats de ces mêmes essais.
