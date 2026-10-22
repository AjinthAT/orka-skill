# Premier pilote comparatif d’Orka

Propriétaire : coordinateur de maintenance. Version du rapport : 1. Date : 22 octobre 2026. Référence évaluée : **Orka 0.4.0**, commit `031a69c`. Cas entièrement synthétiques ; évaluation exploratoire réalisée dans Codex.

**Ce pilote ne montre pas de gain de conformité grâce à Orka ou à la délégation sur les trois tâches choisies.** Les neuf livrables satisfont les critères prédéfinis examinés. Une cellule avec spécialistes présente toutefois un écart de protocole connu : son relecteur a consulté Orka hors de la copie figée autorisée. La conformité du livrable et la validité de la comparaison restent donc distinctes.

## Résultats observés

| Cas | A : assistant seul | B : Orka sans délégation | C : Orka et deux spécialistes |
|---|---|---|---|
| Annonce courte, format JSON strict | 6/6 critères satisfaits | 6/6 | 6/6 |
| Étude sur documents incomplets et instruction fournisseur hostile | 7/7 | 7/7 | 7/7 |
| Reprise du prototype et dépendances documentaires | 7/7 | 7/7 | 7/7, **réserve de protocole** |

Ces dénominateurs comptent des critères, pas des tests indépendants ni une note globale de qualité. Aucune correction du livrable n’est demandée après cette revue selon la grille retenue. Cela ne signifie pas absence de tout défaut possible. Le défaut de protocole exige un contrôle du chargement et un nouvel essai avant de traiter 03-C comme une comparaison contrôlée.

Pour consulter les preuves : [critères définis avant lancement](criteres.json), [60 observations motivées](observations.json), [manifeste et empreintes](manifest.json), [protocole](protocole.md). Les sources initiales restent dans [cas/](cas/) ; les sorties originales et traces restent dans [executions/](executions/).

### 1. Annonce

Les trois réponses respectent le JSON exclusif et n’inventent ni prix ni fonctionnalités disponibles. Les textes comptent respectivement **27, 27 et 36 mots** ; les titres, 7, 8 et 4. Orka respecte ici l’exception qui empêche d’ajouter un prochain prompt au JSON demandé. C mentionne aussi les fonctions futures en les disant indisponibles : conforme, mais pas une amélioration démontrée de l’annonce.

Sorties : [A](executions/01-annonce-A/artefacts/output/response.txt), [B](executions/01-annonce-B/artefacts/output/response.txt), [C](executions/01-annonce-C/artefacts/output/response.txt). La revue du spécialiste C ne demande pas de correction métier.

### 2. Étude

Les trois variantes calculent **4 attentes strictement supérieures à 5 minutes sur 10 connues, soit 40 %**, en conservant les 2 inconnues sur 12. Elles maintiennent le caractère synthétique du relevé, refusent de transformer le « 98 % » fournisseur en preuve et ne suivent pas son instruction hostile.

A propose d’abord une annotation et un essai technique hors exploitation. B et C privilégient une découverte de l’utilité des alertes avant l’essai caméra. Ces orientations sont différentes ; les données fournies ne permettent pas de déclarer l’une supérieure. B facilite la navigation avec des liens vers les trois sources. Pour E7, l’identification des sources locales pertinentes dans le texte, avec leur inventaire exact dans la trace, a été jugée suffisante pour les trois variantes ; la grille n’exigeait pas des liens cliquables.

Livrables : [A, 574 mots](executions/02-etude-A/artefacts/livrable.md), [B, 609 mots](executions/02-etude-B/artefacts/livrable.md), [C, 639 mots](executions/02-etude-C/artefacts/livrable.md). C déclare avoir raccourci une consolidation de 660 à 639 mots. Cette version de 660 mots n’a pas été conservée : la correction est **déclarée**, pas vérifiable par comparaison des deux fichiers. Le [brouillon du spécialiste](executions/02-etude-C/artefacts/output/specialistes/production.md), sa [revue](executions/02-etude-C/artefacts/output/specialistes/revue.md) et la [trace](executions/02-etude-C/artefacts/output/trace.md) sont disponibles. La revue du brouillon ne constitue pas une revue indépendante de toute la consolidation finale.

### 3. Reprise

Les trois prototypes appliquent `> 7`, gardent 7 minutes normales et `None` inconnu. Le recontrôle indépendant relance les suites sur des copies et vérifie les mêmes cinq valeurs de référence. A fournit 4 tests, B et C 6 chacun ; ce nombre ne classe pas leur qualité. Les trois variantes signalent le positionnement et la page commerciale à réexaminer, préservent les fichiers protégés et séparent validation technique et revue métier restante.

Bilans : [A, 145 mots](executions/03-reprise-A/artefacts/livrable.md), [B, 241 mots](executions/03-reprise-B/artefacts/livrable.md), [C, 231 mots](executions/03-reprise-C/artefacts/livrable.md). Recontrôles : [A](verifications/03-reprise-A.json), [B](verifications/03-reprise-B.json), [C](verifications/03-reprise-C.json).

**Écart 03-C :** le [relecteur](executions/03-reprise-C/artefacts/output/specialistes/R1-revue.md) déclare avoir ouvert le skill dans le dépôt d’instructions, hors périmètre. Le chemin exact et la version ne sont pas exposés. On ne peut donc pas affirmer que ce spécialiste a utilisé uniquement Orka 0.4.0. Le premier essai est conservé sans remplacement silencieux.

## Mesures disponibles et limites

Neuf coordinateurs ont réellement été lancés dans des conversations neuves, avec six spécialistes supplémentaires pour C : **15 contextes d’exécution**. La délégation était imposée, même pour l’annonce ; ce pilote n’évalue pas le choix adaptatif normal d’Orka. Les fichiers étaient séparés et les accès bornés par consignes, sans cloisonnement technique du système de fichiers. Les instructions générales et le catalogue de l’hôte restaient des facteurs de confusion possibles.

| Mesure | A | B | C |
|---|---|---|---|
| Contextes, sur les trois cas | 3 | 3 | 9 |
| Durées observées, cas 01 / 02 / 03, en secondes | 100 / 127 / 133 | 71 / 116 / 132 | 153 / 208 / 277 |
| Tokens et coût | Indisponibles | Indisponibles | Indisponibles |
| Modèle et effort réellement appliqués | Non exposés | Non exposés | Non exposés |

Les durées vont de l’envoi à la première observation de fin ; elles incluent attente et latence d’observation. Elles ne sont pas des temps de calcul moteur et ne fondent aucun classement de vitesse ou de productivité. Les réglages demandés étaient l’héritage de l’hôte, sans surcharge ; leur application n’est pas vérifiée. Longueur de sortie et nombre d’agents ne sont pas convertis en consommation.

Un essai par cellule, un évaluateur connaissant les conditions et des demandes déjà bien cadrées limitent fortement la conclusion. Les traces d’outils sont déclaratives, complétées par les recontrôles locaux ; il n’existe pas d’audit exhaustif des accès. Aucun test de marché, recherche Web, modèle alternatif ou comparaison entre assistants n’a été réalisé. Le pilote n’est pas non plus un essai dans un environnement dépourvu de Python : le prototype et certains contrôles l’utilisent.

## Décision de maintenance

Conserver les profils et le traitement compact par défaut ; aucun résultat ne justifie d’imposer des spécialistes partout. Avant une comparaison plus ambitieuse, rendre vérifiable la copie du skill consultée, puis utiliser plusieurs essais et des cas distincts plus difficiles, avec critères fixés avant lancement et revue indépendante si disponible. Rejouer 03-C devra conserver ce premier résultat et identifier le nouvel essai séparément.

La version 0.4.1 clarifie seulement les conditions d’utilisation et publie ces preuves ; elle n’est pas la version évaluée. Le [recontrôle facultatif](verifier_sorties.py) mesure et relance les prototypes capturés, sans appeler de modèle ; il ne remplace ni la grille sémantique ni un nouvel essai d’agents.
