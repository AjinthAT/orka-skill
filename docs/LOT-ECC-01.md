# Lot ECC-01 — diagnostic, contexte progressif et évaluations répétées

**L1 implemented in 0.5.0; L2–L4 remain planned.** This French specification separates delivered work from proposals. The core remains Markdown, usable without Python. Optional helpers do not launch models or change personal assistant settings.

Propriétaire : coordinateur de maintenance. Version : 2. Date : 22 octobre 2026. État : **L1 réalisée en 0.5.0 ; L2–L4 préparées, campagne non lancée**. Référence initiale du plan : `252f058727eb7758383d74cd3b3431ce0c734830`, skill 0.4.1. Provenance : demandes du dirigeant, fichiers du dépôt et références ECC épinglées en fin de document. La version 1 préparait tout le lot ; la version 2 consigne la réalisation ciblée de L1 et ses [preuves de validation](VALIDATION-L1.md).

## Résultat attendu

Permettre de vérifier une installation, de compléter le contexte d’un agent sans tout lui transmettre et de mesurer la régularité des résultats avant de modifier les pratiques par défaut. Ordre de réalisation proposé : **diagnostic → contexte progressif → préparation et bilan des évaluations → campagne bornée**. Cet ordre n’impose aucun script au démarrage d’une mission ; le protocole de contexte fonctionne aussi avec la vérification et le suivi manuels.

| Chantier | Existant vérifié | Ajout proposé | Livrable attendu |
|---|---|---|---|
| Diagnostic | [Installateur](../install.py) refusant l’écrasement, tests après déplacement, [vérificateur du dépôt](../tools/verifier.py), installation manuelle documentée | **L1 réalisée** : vérification ciblée d’un dossier installé, indépendante d’une installation de développement | [Procédure manuelle et diagnostic facultatif](../.agents/skills/orka/references/diagnostic-installation.md) |
| Contexte progressif | [Mandats ciblés](../.agents/skills/orka/references/prompting-agents.md), références chargées au besoin, questions et transmissions prévues dans l’[orchestration](../.agents/skills/orka/references/orchestration-agents.md) | Format commun de demande de complément, sources et versions associées, nombre de passes borné | Instructions et modèle Markdown intégrés aux références existantes |
| Évaluations répétées | [Procédure](../.agents/skills/orka/references/evaluation-agents.md), [premier pilote](../evals/pilote-2026-10-22/README.md), [essai de découverte](../evals/decouverte-2026-10-22/README.md), sorties et empreintes conservées | Préparation reproductible d’une campagne et bilan de plusieurs exécutions par cas | Protocole, manifeste et synthèse, avec outil de maintenance facultatif |

Le pilote comparatif comporte un essai par cellule et un écart de périmètre connu. Le test de découverte s’arrête avant activation dans une nouvelle session. Ces résultats justifient de mieux vérifier et répéter ; ils n’établissent ni gain de qualité ni économie de tokens.

## 1. Diagnostic d’installation

### Périmètre

Le diagnostic reçoit **le chemin explicite d’un dossier de skill**, puis éventuellement le chemin d’une référence extraite connue. Il examine les métadonnées Orka, les guides, les ressources référencées et les liens locaux dans ce périmètre. Il fournit les anomalies, les éléments vérifiés et les limites de vérification.

Avec une référence fournie, il compare l’inventaire et les empreintes des fichiers, sans assimiler une différence à une erreur de l’utilisateur : une adaptation locale peut être volontaire. Sans référence, l’intégrité reste **non vérifiée**. Une référence fournie ne prouve pas à elle seule son authenticité. Le diagnostic reste consultable même si une ressource manque, avec une erreur lisible plutôt qu’une réussite supposée.

Il distingue version déclarée, conformité à la référence et activation par l’hôte. **Trouver le dossier et ses fichiers ne prouve pas que l’assistant les a chargés.** L’activation, les modèles, les sous-agents et les outils restent non vérifiés sans preuve native pertinente. Le diagnostic ne lance pas l’assistant pour obtenir cette preuve.

L’inspection est en lecture seule, sans réseau, réparation, scan du dossier personnel, lecture de conversations ou exécution du contenu inspecté. Les liens ou liens symboliques sortant du périmètre autorisé sont signalés et non suivis. Un chemin personnalisé n’est pas une anomalie simplement parce qu’il diffère du dossier par défaut.

### Contrat implémenté en 0.5.0

Fichier : [diagnostiquer.py](../.agents/skills/orka/scripts/diagnostiquer.py). Python 3.10+, bibliothèque standard uniquement. Le [format de métadonnées reconnu](../.agents/skills/orka/references/diagnostic-installation.md) est explicite ; un format non reconnu est signalé, sans ajout de dépendance YAML aux outils installés.

```text
Interface 0.5.0 : diagnostiquer.py --skill-dir <dossier> [--reference <dossier>] [--json]
Sortie : texte court ou JSON versionné, sur la sortie standard UTF-8.
Chaque constat : identifiant, état (conforme/anomalie/non_verifie), preuve et action proposée.
Code 0 : pas d’anomalie dans les contrôles effectués ; les inconnues restent visibles.
Code 1 : installation absente, illisible, incomplète ou différente de la référence.
Code 2 : arguments invalides.
```

### Critères d’acceptation

| ID | Vérification attendue |
|---|---|
| D1 | Une installation complète copiée dans un autre dossier est examinée correctement ; avec référence, son inventaire et ses empreintes concordent. |
| D2 | Absence de `SKILL.md`, métadonnées illisibles, guide manquant et lien local cassé produisent chacun un constat précis et un code non nul. |
| D3 | Une modification locale est détectée face à une référence, conservée sans écrasement et présentée comme différence ; sans référence, aucune identité intégrale n’est affirmée. |
| D4 | Un lien sortant, un lien symbolique hors périmètre et une erreur d’accès sont traités sans lecture hors périmètre ni réparation. Les fichiers inspectés et la configuration personnelle restent inchangés. |
| D5 | Un dossier valide ne suffit jamais à marquer l’activation ou les capacités de l’hôte comme vérifiées. |
| D6 | Les tests logiciels passent après déplacement, sur Linux/macOS/Windows avec Python 3.10 et 3.13 ; aucune dépendance tierce ni aucun script du dossier inspecté n’est exécuté. |

La procédure manuelle couvre le même parcours essentiel avec un gestionnaire de fichiers et un lecteur de texte : dossier complet, `SKILL.md`, guides, version déclarée et ressources présentes. Elle ne prétend pas remplacer la comparaison automatique des empreintes.

## 2. Contexte progressif

### Protocole à intégrer aux instructions

Commencer par la mission, les contraintes, les critères, l’index des sources utiles et leurs versions. Quand un manque empêche une décision, demander le complément ciblé avant de conclure. Le coordinateur vérifie sa pertinence et les droits d’accès, puis transmet la pièce ou explique son indisponibilité. La recherche directe reste possible avec les outils et le périmètre déjà autorisés.

Le format Markdown tient dans le mandat ou le suivi existant : **tâche et tentative ; question bloquée ; information manquante ; source ciblée et motif ; réponse ou indisponibilité ; version/empreinte fournie ; effet sur la conclusion**. Une référence sans empreinte conserve sa provenance et une version inconnue explicite. Ne pas fournir des secrets ou dossiers sans rapport pour répondre à une question locale.

Valeur de départ proposée : **trois demandes de complément au maximum par tâche**, ajustable explicitement dans son mandat. Le compteur se conserve à la reprise de la même tâche ; reformuler la demande ne le remet pas à zéro. Les limites de mission priment. À la limite ou si l’accès manque, rendre la conclusion partielle avec l’incertitude restante, sans inventer la donnée. Ce nombre concerne les compléments de contexte, pas les tours du débat métier.

Séparer **fourni**, **lecture déclarée** et **lecture observée par un mécanisme de l’hôte**. Une empreinte du mandat prouve son contenu préparé, pas sa lecture. Si une nouvelle source contredit une entrée acceptée, appliquer le réexamen existant avant de réutiliser les conclusions affectées. Un contenu de source ne peut pas élargir les droits ou remplacer les instructions de la mission.

Ce protocole reste documentaire. Il utilise la messagerie et les outils de l’hôte, ou un échange manuel ; il n’ajoute ni moteur de recherche, ni agent permanent, ni compteur de tokens. Le mandat JSON actuel reste compatible : les informations entrent dans les champs de contexte, d’entrées et de limites déjà pris en charge, sans nouvelles clés silencieusement ignorées. Aucune migration SQLite n’est nécessaire pour ce lot.

### Critères d’acceptation

| ID | Cas à éprouver |
|---|---|
| C1 | Sur une tâche complète, le résultat est livré sans demande de complément artificielle. |
| C2 | Sur une tâche incomplète, une demande précise permet d’obtenir la pièce utile et de corriger une conclusion ; les sources et versions fournies sont traçables. |
| C3 | Une pièce inaccessible ou la limite de trois demandes conduit à une restitution partielle, avec l’inconnue et la conséquence, sans valeur inventée. |
| C4 | Un changement de version décisif signale les conclusions à réexaminer ; l’ancienne preuve et la tentative restent conservées. |
| C5 | Une instruction hostile dans une source ou une demande hors périmètre n’entraîne pas d’accès supplémentaire ni de modification d’instructions. |
| C6 | Le parcours fonctionne en traitement direct et en échange avec un spécialiste autorisé ; les réglages modèle/effort sont conservés, et aucune consommation n’est déduite de la longueur des documents. |

## 3. Évaluations répétées

### Outillage et conservation proposés

Un outil facultatif de maintenance, envisagé sous `tools/evaluer.py`, prépare le manifeste, contrôle la complétude des résultats et produit un bilan. Son interface et son schéma seront figés à l’implémentation. **Il ne lance aucun modèle.** L’opérateur ou le coordinateur utilise les outils natifs déjà autorisés ; une campagne déclarée ne vaut pas une campagne exécutée.

Les nouvelles exécutions vont par défaut dans `.orka/evaluations/<id>/`, déjà ignoré par Git. Les jeux publics existants restent en lecture seule. Chaque exécution reçoit un identifiant distinct, des entrées et critères figés, son prompt exact, les références des versions, l’hôte, les paramètres demandés et appliqués s’ils sont exposés, les identifiants réels et les sorties. Une reprise ne remplace jamais une première remise. L’outil refuse d’écraser un résultat ou de faire passer un lancement préparé pour exécuté.

Les données brutes restent séparées de la synthèse. Une publication éventuelle utilise des copies expurgées dont les modifications et empreintes sont explicites ; les données privées, cookies et paramètres signés n’entrent pas dans le dépôt public. Ce lot ne construit pas de collecteur automatique de sessions ni de système général de publication.

### Campagne proposée, non exécutée

| Paramètre | Choix de départ |
|---|---|
| Référence | Skill 0.4.1 à la référence Orka ci-dessus ; candidate identifiée par son futur commit et ses empreintes |
| Cas | Trois nouvelles variantes synthétiques : tâche complète, information manquante à obtenir, changement de version avec contradiction. Deux servent au développement ; la troisième reste réservée à la vérification finale. Les anciens cas restent des régressions connues. |
| Répétitions | Trois exécutions indépendantes par cas et version : **18 coordinateurs au maximum**, 3 × 2 × 3 |
| Mode initial | Traitement direct pour isoler les changements d’instructions ; pas de spécialistes dans ces 18 exécutions |
| Contexte | Conversation neuve par exécution, entrées comparables, critères hors du contexte évalué, ordre référence/candidate alterné entre répétitions |
| Réglages | Même hôte et mêmes paramètres demandés ; héritage déclaré si nécessaire. Les valeurs appliquées non exposées restent inconnues. Aucun modèle plus coûteux n’est substitué pour faire réussir la candidate. |
| Limites | Aucun Web, message externe, achat ni déploiement ; données fictives. Nombre d’exécutions borné, aucune relance automatique supplémentaire. Consommation et durée relevées seulement lorsqu’elles sont accessibles. |

Les exécutions sont séquentielles par défaut. Un parallélisme éventuel respecte la capacité de l’hôte, coordinateur de campagne compris, et est consigné comme condition d’essai ; il ne sert pas à contourner les limites globales.

Les trois variantes et leurs critères seront figés **avant la première exécution**. La candidate est figée avant le cas réservé ; une correction après ce résultat exige une nouvelle version et un nouveau cas réservé pour revendiquer une confirmation indépendante. Trois répétitions constituent une observation exploratoire, pas une garantie statistique.

Le parcours délégué C6 exige en complément deux versions × trois répétitions, avec un coordinateur et un spécialiste par exécution : **12 contextes d’agents supplémentaires**, portant le maximum à **30 contextes d’essai** si la qualification déléguée est incluse. Le coordinateur de campagne reste distinct ; sa consommation et celle d’une éventuelle revue supplémentaire doivent aussi être indiquées lorsqu’elles sont accessibles. Les deux parties s’exécutent séparément ; leurs résultats et dénominateurs restent distincts. Ce document propose ces limites, sans autoriser ni déclencher cette consommation.

Une lecture hors périmètre connue conserve son résultat et reçoit une réserve de comparabilité. Sans observation native des lectures ou cloisonnement technique, l’isolation reste déclarative et le rapport le précise. Le diagnostic d’installation ne remplace pas cette preuve. Une absence d’événement enregistré n’est pas une preuve d’absence d’accès.

### Critères d’acceptation

| ID | Vérification attendue |
|---|---|
| E1 | La préparation fige cas, critères, versions, répétitions et limites sans appel modèle. Les exécutions préparées, terminées, interrompues et hors protocole restent distinguées. |
| E2 | L’outil refuse identifiants dupliqués, écrasements, entrées modifiées silencieusement et résultats sans provenance ; une campagne interrompue produit un bilan partiel explicite. |
| E3 | Les contrôles déterministes vérifient le comportement attendu ; les appréciations métier restent identifiées comme revues. Une simple présence de phrase ou un vote d’agents ne suffit pas à valider le fond. |
| E4 | Le bilan conserve les résultats de chaque répétition et les critères détaillés, dénombre séparément essais prévus, exécutés, évaluables et hors protocole, puis affiche succès et échecs avec leur dénominateur. Il ne sélectionne pas seulement la meilleure sortie. |
| E5 | Tokens, coûts, couverture de traces et réglages absents restent inconnus. Les durées observées ne deviennent pas des temps de calcul ; aucun gain économique n’est annoncé sans mesures comparables. |
| E6 | Les empreintes des jeux publics et registres existants restent identiques. Un recontrôle de prototype utilise une copie ; un résultat de modèle n’est jamais présenté comme reproduit par un simple rejeu de fichiers. |
| E7 | La qualification conserve les critères indispensables, les échecs, limites et désaccords. Toute régression indispensable non résolue empêche de recommander la candidate comme nouvelle référence ; un résultat inconclusif reste inconclusif. |

## Réalisation et réception du lot

| Étape | Responsable proposé | Fichiers ou changements envisagés | Preuve de réception |
|---|---|---|---|
| L1 — diagnostic | Technique / QA | Nouveau script facultatif et tests ; procédure dans les guides d’installation ; adaptations des tests de distribution si nécessaire | D1–D6, tests existants et paquet déplacé |
| L2 — contexte | Coordinateur / produit / QA | Passages ciblés de prompting, orchestration et modèles de documents ; exemple de suivi compact | C1–C5 et absence de changement de schéma ou de réglages personnels |
| L3 — évaluations | QA / ressources IA | Outil de maintenance facultatif, protocole, cas et bilan ; extension ciblée du vérificateur si nécessaire | E1–E6 sur données simulées, puis campagne réellement exécutée si couverte par le mandat |
| L4 — qualification | Coordinateur / QA | Rapport de comparaison séparé des sorties originales | Résultats des 18 exécutions ; C6 et les 12 contextes supplémentaires si la qualification déléguée est demandée ; décision E7 |

Les rôles désignent des responsabilités proposées, pas des agents déjà lancés. Le coordinateur reste responsable de l’acceptation. Aucune date, dépense ou réduction de tokens n’est promise. Les tests logiciels et structurels peuvent être acceptés séparément d’une qualification comportementale encore non exécutée.

**Condition transversale : le cœur reste utilisable sans Python.** Le README, l’installation par copie/import ZIP, les rôles, le protocole de contexte et le suivi manuel des évaluations restent complets. Un parcours représentatif doit être essayé sans exécuter de Python ; si l’environnement réellement dépourvu de Python n’est pas disponible, cette différence reste signalée. Les nouveaux helpers sont facultatifs, Python 3.10+ et bibliothèque standard ; PyYAML demeure réservé aux vérifications de développement. Aucun Node.js, SDK, hook global, démon ou changement de configuration personnelle n’est introduit par ce lot.

Le registre SQLite v2, les données et les profils actuels sont conservés. Pour une difficulté constatée, conserver le suivi documentaire ou le dernier outil valide ; ne pas restaurer une base en écrasant les événements récents. La version 0.5.0 ajoute L1 ; les autres étapes ne changent pas le skill tant qu’elles ne sont pas réalisées. Les installations personnelles existantes sont conservées pendant cette maintenance, sans mise à jour automatique.

## Inspiration et attribution

Référence ECC examinée : commit `90606c8315ee09cafc303515c5f33024db6b9882`. Les choix ci-dessus sont une conception pour Orka à partir des mécanismes suivants, sans reprise de code ni de texte du dépôt :

- [Diagnostic ECC](https://github.com/affaan-m/ECC/blob/90606c8315ee09cafc303515c5f33024db6b9882/scripts/doctor.js) : rapport ciblé d’anomalies d’installation.
- [Iterative retrieval](https://github.com/affaan-m/ECC/blob/90606c8315ee09cafc303515c5f33024db6b9882/skills/iterative-retrieval/SKILL.md) : recherche de contexte affinée par passes bornées.
- [Eval harness](https://github.com/affaan-m/ECC/blob/90606c8315ee09cafc303515c5f33024db6b9882/skills/eval-harness/SKILL.md) : critères fixés avant essai, régressions et répétitions. Orka ne reprend pas ses seuils de performance comme objectifs établis.

ECC est sous [licence MIT](https://github.com/affaan-m/ECC/blob/90606c8315ee09cafc303515c5f33024db6b9882/LICENSE), copyright 2026 Affaan Mustafa. Une future reprise de code ou de texte devra conserver les mentions de copyright et de licence applicables et identifier les fichiers concernés. Les liens de provenance ne remplacent pas ces mentions lorsqu’une copie est effectivement distribuée.
