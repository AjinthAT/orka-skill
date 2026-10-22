# Évaluer et faire évoluer les agents

Ce processus concerne les changements de prompt, de rôle, de profil modèle/effort et de méthode de coordination. Il complète [la validation](validation.md) et [la gestion documentaire](gestion-documentaire.md). Les tests locaux du préparateur vérifient son comportement logiciel ; ils ne mesurent pas la qualité des agents ni le gain économique des profils.

## Constituer des cas utiles

Conserver des cas représentatifs des missions attendues : demande claire, information manquante, contradiction, correction, reprise et transmission entre équipes. Ajouter les échecs réellement observés, en retirant les données privées inutiles et en respectant les autorisations de conservation.

Un cas précise : identifiant, origine réelle ou simulation, entrées et versions, résultat recherché, critères observables, erreurs à détecter et actions interdites ou hors mandat. Un cas simulé reste signalé ; il ne devient pas une preuve de marché.

Prévoir des cas auxquels une réponse utile est possible et des cas nécessitant une réserve ou une question. Un agent qui refuse tout ne doit pas obtenir un bon résultat simplement parce qu'il évite les erreurs.

## Comparer une version de référence et une candidate

1. Définir l'hypothèse : défaut à corriger ou amélioration recherchée, avec la mesure pertinente. Conserver la version de référence et les identifiants des configurations.
2. Choisir les cas de développement et réserver des cas distincts pour la vérification finale lorsque le jeu le permet. Ne pas inclure la réponse attendue dans le prompt de production. Éviter d'ajuster sans cesse une version sur les mêmes exemples puis de les présenter comme une évaluation indépendante.
3. Définir avant comparaison les critères indispensables, les erreurs rédhibitoires dans le périmètre et les limites de coût ou durée connues. Ne pas inventer un seuil universel ou un budget disponible.
4. Exécuter les mêmes cas avec des entrées et outils comparables. Enregistrer versions, empreintes, paramètres demandés et paramètres appliqués s'ils sont observables. Si un accès ou une donnée change, signaler le facteur de confusion.
5. Examiner les résultats par critère avec les preuves. Une revue par un autre agent peut repérer des défauts ; son accord ne remplace pas les faits ni une vérification métier. Déclarer la méthode et ses limites.
6. Décider de conserver la référence, corriger la candidate ou l'essayer sur un périmètre borné. Une amélioration sur quelques cas ne suffit pas à annoncer une supériorité générale.

Ces exécutions nécessitent les outils et autorisations correspondants. Distinguer une procédure disponible des essais réellement consignés ci-dessous.

## Premier pilote exécuté : Orka 0.4.0, 22 octobre 2026

Le [rapport public et ses preuves](https://github.com/AjinthAT/orka-skill/blob/main/evals/pilote-2026-10-22/rapport.md) conserve trois cas synthétiques : annonce JSON, étude documentaire incomplète et reprise après changement de décision. Neuf coordinateurs en contextes neufs comparent assistant seul, Orka sans délégation et Orka avec deux spécialistes imposés par cas. Six spécialistes ont effectivement été lancés ; les sorties, critères prédéfinis, empreintes, observations et recontrôles sont conservés dans le dépôt, hors du paquet installé.

Les neuf livrables satisfont les critères examinés, sans gain de qualité établi. Une revue du cas 03-C a consulté Orka hors de la copie figée : son résultat fonctionnel est conservé avec une réserve de comparabilité. Une correction interne de longueur du cas 02-C est déclarée, mais sa version intermédiaire n'a pas été conservée. Les tokens, coûts et réglages réellement appliqués ne sont pas exposés. Les durées incluent la latence d'observation. Un essai par cellule, une revue non aveugle, les consignes communes de l'hôte et l'absence de cloisonnement technique empêchent de conclure à une supériorité générale. Aucun réglage de profil n'est modifié sur cette base.

La maintenance 0.4.1 clarifie les guides : instructions et installation manuelle sans Python ; scripts locaux et contrôles du dépôt facultatifs, avec leurs prérequis. Ce pilote ne constitue pas un essai sans Python ni une qualification de tous les assistants.

## Retour d'usage : restitution et lecture courante, version 0.1.1

Une revue utilisateur d'un dossier multi-agents a révélé une lecture principale trop longue, des propositions initiales mêlées à leurs remplaçantes et des liens internes dépendant d'un ordinateur. Référence avant correction : commit `25c7e15`. Hypothèse de maintenance : une synthèse d'une page, des références courantes uniques, un historique séparé et des liens relatifs rendent la décision plus accessible sans retirer les preuves.

La correction des instructions a été appliquée éditorialement au dossier local autorisé, dont l'état précédent a été préservé. Contrôles : contenu de la synthèse et limites, présence des propositions initiales et réponses conservées, résolution des liens après copie, règles chiffrées conservées. Aucun contenu privé de mission n'est inclus dans ce dépôt. Ce contrôle sur un cas connu n'est ni un nouvel essai d'agents ni une comparaison indépendante des modèles. Les scénarios distincts de [validation](validation.md) restent à exécuter pour mesurer la généralisation ; aucun gain chiffré n'est revendiqué.

## Évolution 0.2.0 : ressources IA, vision et identité

Référence avant changement : commit `35f2a61`. Correction de portée demandée par le dirigeant : RH orientée agents IA plutôt que personnel humain par défaut ; allocation par tâche et suivi d'usage observable, sans second orchestrateur. Ajout de guides conditionnels pour vision/preuves/innovation et noms/domaines ; identifiants des rôles conservés. Vérifications prévues : préparation de tous les rôles et de profils explicites, refus des réglages incompatibles, liens, paquet installable et cohérence des limites annoncées. Les cas de validation ajoutés décrivent les comportements à éprouver ; ils ne sont pas une campagne de modèles exécutée. Aucun gain de tokens ou de qualité n'est établi par la rédaction.

## Évolution 0.3.0 : expériences et bilan local

Référence avant changement : commit `bfe1c68`. Ajouts demandés : lier hypothèses, essais et décisions ; éprouver faisabilité et adoption ; analyser les résultats et moyens des agents. Le guide des expériences reste documentaire. Le bilan JSON est un logiciel local sur relevés fournis, sans collecteur ni décision automatique sur les profils.

Contrôles exécutés : 8 tests du nouveau bilan sur données simulées (inconnues, dénominateurs, reprises, sous-totaux, devises, doublons et lecture sans écriture), avec les 29 tests des outils existants après installation dans un dossier temporaire ; 7 tests de distribution, validation du format du skill et résolution des liens locaux. Ces contrôles vérifient le logiciel et la structure. Aucun essai d'agents métier, entretien, prototype terrain ou gain de qualité/coût n'est établi par cette maintenance.

## Mesures et preuves

Maintenance 0.6.0, référence `dd72cb7` : réception ciblée du contexte progressif, avec trois cas fictifs en contextes neufs, une exécution chacun et cinq remises conservées. Le [rapport et les preuves publiques](https://github.com/AjinthAT/orka-skill/blob/main/evals/contexte-L2-2026-10-22/README.md) relient C1–C5 aux résultats : tâche complète, complément de prix, changement de version et reprise au plafond avec source hostile. Les critères et les instructions ont été figés avant les essais. Aucun réglage modèle/effort n'a été modifié. La comparaison avec 0.5.0 reste documentaire ; la référence n'a pas été exécutée sur ces cas. Les lectures sont déclarées, sans audit indépendant des accès. Ces observations ne remplacent ni C6 ni la campagne répétée L4 et ne prouvent aucun gain de qualité ou de coût.

Maintenance 0.4.0, référence `7a61a35` : stabilisation des dépendances transitives, versions d'entrées figées par tentative, réexamen et migration explicite v1 vers v2 avec sauvegarde. Les nouveaux cas logiciels couvrent trois niveaux de dépendance, une source réacceptée à contenu identique, les limites et rédacteurs, la conservation des preuves, les bases avec réservations actives, le journal WAL et l'annulation d'une migration en échec. Les régressions UTF-8 utilisent des CLI sous configuration ASCII. Le dépôt fournit une commande de vérification et une matrice CI ; ces tests de logiciel ne mesurent pas un gain métier ou une supériorité des profils.

Maintenance 0.3.1, référence `e46ea51` : ajout demandé de guides installables bilingues et d'un prochain prompt adapté en fin de réponse. La distribution et les chemins affichés sont vérifiés par les tests d'installation ; les scénarios documentent les exceptions de format, les blocages et l'absence de suite immédiate. Aucun essai de modèle ne prouve à ce stade l'application systématique du prompt final par tous les assistants.

Le [bilan local](bilan-agents.md) aide à calculer les indicateurs disponibles à partir des tentatives et mesures fournies. Les données absentes, la couverture et la méthode d'acceptation restent visibles ; le script ne qualifie pas automatiquement un profil. Pour relier une comparaison à une hypothèse et à une décision, réutiliser le suivi des [expériences](experiences-apprentissage.md).

| Question | Mesure possible et précaution |
|---|---|
| Le résultat sert-il la mission ? | Critères satisfaits et tâches effectivement accomplies, avec dénominateur et cas incomplets. |
| Les affirmations sont-elles étayées ? | Erreurs factuelles confirmées, sources inadéquates et affirmations non vérifiées, distinguées. |
| L'agent respecte-t-il le mandat ? | Actions hors périmètre observées et corrections de dérive ; ne pas compter une simple proposition comme une action exécutée. |
| Combien faut-il reprendre ? | Retours de correction et acceptations à la première revue sur les tâches réellement revues. |
| Quels sont les moyens consommés ? | Durée et consommation réellement accessibles ; valeurs absentes marquées indisponibles. |
| Le résultat tient-il face aux cas difficiles ? | Réponses aux entrées contradictoires, données manquantes et tentatives d'instructions externes, avec constat explicite. |

Ne pas confondre longueur de réponse, confiance affichée et qualité. Pour une estimation de coût, fournir les mesures d'usage et la tarification vérifiée applicables ; ne pas convertir automatiquement une limite de jetons en coût certain.

## Promouvoir, surveiller et revenir à la référence

Une modification est retenue selon le mandat de maintenance et les critères définis, sans obligation d'obtenir une nouvelle permission pour une correction déjà autorisée. Préserver la version de référence avant un changement substantiel ; sans moyen de la préserver, ne pas prétendre disposer d'un retour arrière.

Un essai limité garde sa portée, ses critères d'arrêt et un responsable. En cas de défaut, revenir à la version connue uniquement si cela reste adapté et autorisé ; une restauration du prompt n'annule pas les actions déjà effectuées par un agent. Vérifier séparément les conséquences externes éventuelles.

Tenir une trace concise : changement, motif, cas utilisés, résultats, limites, décision et référence précédente. Le coordinateur peut proposer des améliorations ; une mission opérationnelle ne modifie pas spontanément les règles globales.

## Renforcements suivants à implémenter

| Priorité | Renforcement | Résultat attendu | État actuel |
|---|---|---|---|
| Haute | Supervision persistante des tâches et agents | Conserver l'état, signaler l'inactivité et empêcher deux réservations actives sur une même sortie. | [Registre local implémenté](supervision-locale.md), testé sur données simulées ; lancement, arrêt et alertes continues restent à raccorder. |
| Haute | Contrôle effectif des moyens et outils | Appliquer les limites globales et autorisations dans le moteur, au lieu de compter sur le seul texte des prompts. | Capacité et tentatives contrôlées dans un même registre ; coûts financiers et droits techniques des outils restent hors de ce contrôle. |
| Haute | Évaluations sur des missions représentatives | Vérifier les prompts et profils sur des résultats observés avant de modifier les réglages par défaut. | Premier pilote synthétique exécuté sur 3 cas et 3 conditions ; un écart de protocole connu. Répétitions, cas plus difficiles et comparaison des profils restent à réaliser. |
| Haute | Essais isolés des opérations extérieures | Préparer et vérifier publication, envoi ou déploiement dans un environnement adapté, avec des contrôles empêchant les effets réels pendant l'essai. | La préparation locale n'exécute rien ; aucun environnement de test d'opérations extérieures n'est configuré. |
| Moyenne | Journal des opérations et reprises | Reconnaître les tentatives, les résultats reçus et les actions au résultat incertain sans les répéter aveuglément. | Événements et requêtes persistés dans le registre ; contrôle des actions extérieures à implémenter. |
| Moyenne | Bibliothèque de connaissances validées | Retrouver faits et décisions de référence avec provenance, portée et versions, puis réexaminer ce qui a changé. | Conventions documentaires disponibles ; contenu métier à constituer pendant les missions. |
| Moyenne | Tableau de pilotage alimenté par les exécutions | Voir travaux, blocages, vérifications et consommation réelle, sans données inventées. | Bilan local implémenté sur relevés fournis ; collecte automatique et interface à construire. |

Prioriser les développements selon les défauts et besoins réellement observés. Aucun de ces ajouts ne justifie de multiplier les agents ou les données collectées sans utilité pour la mission.
