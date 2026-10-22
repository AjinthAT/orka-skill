# Piloter une mission efficacement

Ces règles organisent le travail des rôles existants ; elles n'ajoutent aucun poste. Les limites fixées par le dirigeant et l'environnement priment sur les valeurs proposées ici.

## Adapter l'effort au résultat attendu

| Situation | Organisation | Trace suffisante |
|---|---|---|
| Livrable simple, autonome et facile à vérifier | Un responsable ; contrôle direct ; pas de débat par défaut. | Un `mission.md` regroupant objectif, résultat et vérification, ou une entrée dans le suivi existant. |
| Plusieurs livrables ou dépendances entre équipes | Coordinateur, spécialistes nécessaires et contrôles ciblés. | Brief, plan, état et livrables séparés selon les modèles. |
| Choix incertain à fort impact sur le projet | Analyses initiales séparées, revue critique et arbitrage documenté. | Dossier avec preuves, objections et décision à prendre. |

Une fiche de service n'impose pas de lancer un responsable et ses spécialistes pour une tâche qu'une personne peut réaliser correctement. Un rôle de contrôle supplémentaire se justifie par un risque concret ou une compétence distincte, pas par l'organigramme.

## Adapter aussi la documentation

Choisir les pièces nécessaires à la décision avant de déléguer. Pour une étude, prévoir une synthèse dirigeant d'environ une page, les analyses utiles et leurs preuves ; ajouter les autres documents seulement s'ils servent à exécuter, vérifier ou reprendre le travail. Dans une mission compacte, regrouper ces éléments plutôt que créer une nouvelle arborescence. Préciser aux spécialistes le destinataire et le niveau de détail attendu, sans faire d'un nombre de fichiers ou de mots un indicateur de qualité.

Chaque analyse commence par sa conclusion actuelle et les éléments qui la justifient. Ne pas recopier le brief, les règles communes ou les réserves déjà exposées ailleurs : donner le lien et développer seulement l'apport propre à la tâche. Une condition déterminante doit toutefois rester visible dans une synthèse susceptible d'être lue seule. Si le détail gêne la décision, garder la preuve en annexe et raccourcir la lecture principale sans affaiblir l'analyse.

## Préparer une tâche exécutable

Chaque tâche possède un identifiant unique dans sa mission, un seul responsable du résultat, les entrées et versions utiles, ses dépendances, un livrable distinct et des critères vérifiables. Utiliser le [contrat de tâche](modeles.md) pour les travaux délégués ; une ligne concise suffit pour une tâche simple.

Une demande nouvelle ou un changement de périmètre passe par les [processus communs](processus-transverses.md) pour identifier le bon dossier, l'impact et le mandat applicable. Une précision déjà autorisée ne nécessite pas une nouvelle permission.

Un critère décrit ce que le destinataire pourra constater : message conforme aux fonctions disponibles, calcul reproductible, parcours accepté ou résultat technique observé. « Faire un bon travail » n'est pas un critère.

Avant lancement, vérifier que les entrées nécessaires existent et que les outils sont accessibles. Sinon, marquer la tâche bloquée avec cause et prochain responsable. Une tâche peut partir avec une hypothèse explicite si sa sortie reste utile et si la dépendance sera réexaminée avant acceptation.

## Ordonner et limiter le travail

Traiter d'abord les tâches prêtes qui débloquent les autres, réduisent une incertitude décisive ou répondent à une échéance fournie. Expliciter les compromis quand ces priorités se contredisent. Ne pas inventer un score numérique de priorité sans méthode utile à la mission.

Paralléliser les travaux indépendants. Réserver le livrable amont avant de lancer le travail qui en dépend ; ne pas faire produire simultanément des versions incompatibles. La capacité totale définie dans [la collaboration](collaboration.md) reste un plafond, pas une cible à remplir.

Le coordinateur suit tâches actives, dépendances et limites connues. À une limite atteinte, ne pas ouvrir de nouveaux travaux ni poursuivre hors budget ; préserver les résultats et indiquer les manques. Si les coûts ne sont pas mesurables, le déclarer et appliquer les limites disponibles de temps, tâches et tentatives. Ces règles sont des consignes de session ; leur application automatique exige le moteur décrit dans l'implémentation.

## Accepter sur des preuves

Cycle des tâches : à faire → en cours → à vérifier → terminée. « Bloquée » et « annulée » décrivent des sorties distinctes ; elles ne comptent pas comme des réussites. Une correction remet la tâche à faire et conserve le motif du retour.

L'auteur livre son résultat avec les critères contrôlés et leurs preuves. Le responsable de la réception vérifie la version effectivement remise. Le responsable d'acceptation est nommé dans le mandat ; il peut être le coordinateur ou le responsable de service. Pour un enjeu important, désigner un relecteur distinct de l'auteur si c'est possible et autorisé. Sinon, déclarer un autocontrôle et sa limite, sans l'appeler revue indépendante.

Chaque critère est satisfait, non satisfait ou non vérifié. Une preuve peut être une source consultée, un calcul refait ou un résultat d'exécution selon le travail ; une affirmation de l'auteur ne prouve pas qu'une action a eu lieu.

Un critère indispensable non satisfait ou non vérifié empêche de déclarer la tâche terminée. Rendre le résultat partiel avec sa limite. Un critère hors périmètre n'est retiré qu'avec justification cohérente avec le mandat, sans affaiblir silencieusement l'objectif.

## Corriger sans boucler

Regrouper les défauts dans un retour précis : critère, observation, conséquence et correction attendue. Par défaut, prévoir un passage de correction ciblé pour les contenus et analyses, puis arbitrer les manques persistants. Pour le code, corriger et vérifier selon les consignes du dépôt et les limites de mission ; ne pas présenter une version défaillante comme livrée avec succès.

Une nouvelle tentative technique n'est utile que si la cause paraît transitoire ou si la méthode change de façon justifiée. Une source inaccessible, une autorisation absente ou un effet extérieur incertain ne se résout pas par des relances identiques.

## Préserver les dépendances et améliorer la méthode

Quand une entrée change, identifier les tâches qui l'utilisent et marquer leurs résultats à réexaminer. Reprendre uniquement les parties affectées. Après réattribution, attendre l'arrêt ou la fin de l'ancien rédacteur avant d'autoriser un nouveau rédacteur sur son fichier.

À la fin d'une mission substantielle, relever si les données existent : tâches terminées et bloquées, acceptations dès la première revue, retours de correction, temps observé et consommation mesurée. Calculer le taux d'acceptation initiale sur les seules tâches réellement revues et indiquer le dénominateur. Des métriques absentes restent indisponibles.

Proposer au plus quelques améliorations reliées à un échec ou retard observé. Une seule mission ne démontre pas un gain généralisable. Modifier les instructions globales dans une mission de maintenance qui l'autorise ; le travail opérationnel courant ne réécrit pas le skill de lui-même.
