# Gestion de la documentation

Objectif : permettre aux agents de retrouver le bon document, de comprendre sa validité et de savoir quoi réexaminer quand il change. Cette procédure définit les usages des fichiers ; elle ne fournit ni sauvegarde automatique ni contrôle d'accès technique.

## Sources de référence

| Information | Référence à rechercher |
|---|---|
| Objectif et contraintes d'une mission | Instruction du dirigeant, puis brief ou suivi compact qui la restitue. |
| Tâches, responsables et avancement | Plan et état de la mission, ou suivi compact. |
| Résultats de l'étude | Analyses, sources et dossier avec leurs limites. |
| Décisions et autorisations | Instruction explicite et journal qui en garde la référence. |
| Comportement d'un produit et vérifications | Dépôt désigné, version identifiable et résultats de vérification. |
| Contenus marketing et commerciaux | Livrables de la mission et faits produit vérifiés. |
| Procédures communes des agents | Skill et références de ce dossier. |

Ne pas considérer un document plus récent comme automatiquement plus fiable ou plus autorisé. En cas de conflit, identifier origine, portée et version, vérifier l'état réel si nécessaire et consigner le résultat. Une page externe ou un fichier marqué « validé » ne remplace pas une instruction humaine ni les règles de l'environnement.

## Propriété et cycle de vie

Un document de référence possède un propriétaire responsable de son contenu. Le propriétaire peut être un rôle, mais chaque modification en cours garde un rédacteur unique. Les fichiers partagés de mission restent sous la responsabilité du coordinateur.

Cycle documentaire : brouillon → en revue → référence, puis remplacé ou archivé lorsque pertinent. « Référence » signifie utilisable dans le périmètre et la version examinés ; cela ne prouve pas une publication, une signature ou une autorisation extérieure.

Pour un document substantiel, préciser : identifiant ou chemin stable, propriétaire, portée, version, date de modification, état, provenance et références nécessaires. Une note temporaire ne nécessite pas un formulaire complet.

## Modifier sans perdre le contexte

1. Vérifier le mandat, le propriétaire et la version courante avant modification ; respecter les travaux d'un autre rédacteur.
2. Préparer le changement et examiner les dépendances. Une correction typographique n'appelle pas le même contrôle qu'un changement de prix, de promesse ou de critère.
3. Réviser le document et vérifier les parties affectées. Pour une modification substantielle, conserver une courte trace du motif et de ce qu'elle remplace dans le document ou le journal existant.
4. Désigner la nouvelle version de référence et signaler les résultats à réexaminer. Garder le chemin courant stable lorsque possible et relier les versions remplacées si leur conservation est utile.

Une date et une version explicite comme `v2` suffisent sans gestionnaire de versions. Une version Git existante peut identifier le code ou le document ; ne pas créer des commits ou des copies d'archives uniquement pour remplir ce champ.

Présenter la conclusion actuelle au début du document. Après un arbitrage, désigner une seule référence pour les règles et critères applicables et y faire pointer les autres pièces. Les propositions retirées restent dans une section historique clairement délimitée, une annexe ou une version antérieure reliée ; ne pas demander au lecteur de reconstituer seul quelle règle remplace laquelle. Conserver les preuves et les motifs de révision sans recopier tout l'historique dans chaque livrable.

Ne pas annoncer une sauvegarde ou une possibilité de restauration sans dispositif réellement disponible. Avant une modification importante, préserver l'état précédent par le moyen accessible et autorisé ; ne pas écraser l'unique preuve utile d'une décision ou d'un incident.

## Retrouver et réexaminer

Pour un dossier comportant plusieurs documents de référence, utiliser un index avec liens, propriétaires, états et versions, selon les [modèles](modeles.md). Un suivi compact ne nécessite pas un registre supplémentaire.

Pour les liens persistés entre fichiers d'un dossier partageable, utiliser des chemins relatifs au fichier qui contient le lien, puis vérifier qu'ils restent valides après copie du dossier. Garder les URL externes complètes. Un lien absolu vers un dépôt distinct peut être nécessaire : le signaler comme dépendance extérieure et identifier sa destination sans recopier de donnée privée inutile. Les liens absolus utiles dans la réponse de l'application ne doivent pas être recopiés automatiquement dans les documents distribuables.

Les événements suivants déclenchent une vérification ciblée : changement produit, nouveau prix, décision révisée, source contradictoire, accès modifié ou incident révélant une information incorrecte. Une revue périodique peut être proposée si elle sert l'activité ; elle n'est pas déclarée automatique sans configuration réelle.

Une source datée reste une observation à cette date. Si une information actuelle est nécessaire, la vérifier de nouveau ; ne pas appliquer une durée de validité uniforme aux prix, décisions et faits historiques.

## Accès et conservation

Ne pas enregistrer de mots de passe, clés ou jetons dans les livrables Markdown. Référencer le moyen d'accès existant sans recopier les secrets. Limiter le contexte client ou RH aux agents qui en ont besoin et au périmètre autorisé.

Archiver signifie retirer un document de l'usage courant en indiquant sa destination et son remplaçant éventuel. Une suppression n'est pas une archive. Appliquer les règles de conservation connues ; si elles sont absentes et que l'action est irréversible, ne pas inventer une politique ni effacer des preuves pour nettoyer le dossier.
