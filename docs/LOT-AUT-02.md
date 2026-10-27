# AUT 02 Superviseur facultatif

Propriétaire : coordinateur de maintenance. Version documentaire : 2. Date : 27 octobre 2026. Base examinée pour le cadrage : `a9d4a11`, branche AUT-01 et skill 0.9.0. **Statut : AUT-02A implémenté, qualification initiale hors ligne sur Linux ; AUT-02B reste à construire.** Le [guide exécutable](SUPERVISEUR-LOCAL.md) et la [réception AUT-02A](VALIDATION-AUT-02A.md) précisent le résultat actuel. Cette version actualise le cadrage initial après l'instruction d'implémenter AUT-02A ; les capacités brutes restent la capture préalable.

## Décision de conception

Créer un superviseur local facultatif, dans le même dépôt, raccordé au registre v2 existant. Commencer par un parcours hors ligne avec de vrais sous-processus déterministes : échec observé, arrêt confirmé, seconde tentative autorisée, résultat contrôlé, puis tâche dépendante. Ajouter ensuite un adaptateur Codex CLI derrière la même interface, avec qualification distincte avant tout essai modèle.

Cette séparation répond au besoin d'autonomie sans confondre trois preuves : le contrôle des processus, le raccordement d'une IA et la qualité des décisions de cette IA. AUT-01 fournit la politique de décision ; AUT-02 en raccordera une première boucle d'exécution. Le cœur installé reste portable et sans Python obligatoire. Le superviseur, lui, utilise Python et s'installe ou se lance explicitement.

Le premier lot vise un contrôleur actif à la fois, une tâche exécutée à la fois et un graphe de tâches fixé au départ. Pas de daemon système, interface graphique, cloud, ordonnanceur récurrent ou gestion multi-machine. La reprise du contrôleur est déclenchée explicitement ; un redémarrage au démarrage de la machine serait une extension ultérieure.

## Capacités vérifiées dans cet environnement

Le [relevé brut](AUT-02-CAPACITES.json) conserve les commandes, codes de sortie et limites. Ces observations portent sur cet hôte, son PATH et son Python courant, pas sur tous les environnements d'Orka.

| Moyen | Observation au 27 octobre 2026 | Conséquence |
|---|---|---|
| Python | 3.14.3, Linux x86_64 ; `sqlite3`, `subprocess`, `json`, `asyncio` importables | Un premier contrôleur standard-library est envisageable ; autres versions et plateformes à vérifier |
| Sous-processus | Deux programmes Python de confiance lancés et attendus : sorties 0 et 75, PID retourné identique au PID observé | Création, récupération des sorties et constat de fin disponibles ; aucune boucle de reprise AUT-02 déjà validée |
| Codex CLI | `0.165.0-alpha.1.2`, aide de `exec` et `exec resume` accessible | Adaptateur candidat ; la version alpha devra être enregistrée et requalifiée en cas de changement |
| Authentification CLI | `codex login status` indique une connexion ChatGPT | Statut déclaré par le CLI ; ni accès à un modèle donné, ni quota, ni génération réussie démontrés |
| Interface CLI | Aide locale : `--json`, `--output-schema`, `--output-last-message`, reprise par identifiant | Supports documentés à raccorder ; flux réel non capturé par cette étude |
| Sous-agents natifs de l'hôte | Interfaces de lancement, observation, attente et interruption exposées dans cette session ; utilisées pendant AUT-01 | Utiles en session ; aucun pont Python permanent vers ces outils n'est fourni par le dépôt |
| Claude, Docker, Node | Non trouvés dans le PATH sondé | Aucun choix de conception ne doit les supposer disponibles ici |
| SDK Claude, module `agents`, Inspect | Non trouvés dans le Python sondé | Les prototypes existants ne sont pas utilisables ici sans préparation distincte ; leurs verrous restent préservés |

Aucun secret ni contenu de fichier d'authentification n'a été extrait ou conservé ; seul le statut rendu par le CLI figure dans le relevé. Les commandes d'aide et de statut ne lancent pas de tâche modèle. Aucune installation, aucun conteneur ni nouvel agent IA n'a été lancé pour ce cadrage.

### Documentation du raccordement CLI

Context7 a résolu `/openai/codex`, puis recherché la sortie JSONL, les événements de fin et la reprise. Les exemples proviennent du code source courant ; ils ne prouvent pas l'identité de comportement avec le binaire alpha local. La documentation [mode non interactif](https://learn.chatgpt.com/docs/non-interactive-mode) et la [référence des commandes](https://learn.chatgpt.com/docs/developer-commands?surface=cli), ouvertes le 27 octobre 2026, confirment ces interfaces.

L'adaptateur utilisera une session identifiée explicitement. Il ne choisira pas `--last`, qui pourrait reprendre une autre mission. Les clés `task_name`, `fork_turns` et autres champs du préparateur destinés à l'hôte ne seront pas transmis comme arguments CLI : une traduction explicite est nécessaire. Un événement de fin ou un JSON conforme au schéma n'établit pas la correction métier ; celle-ci reste vérifiée séparément.

## Architecture et responsabilités

| Composant | Responsabilité et autorité |
|---|---|
| Orka portable | Objectif, délégation, arbitrage et conditions d'arrêt définis par AUT-01 |
| Registre v2 existant | Référence des tâches, dépendances, tentatives, réservations et acceptations |
| Contrôleur facultatif | Réserver, lancer, suivre, arrêter si possible, vérifier et appliquer les transitions autorisées |
| Adaptateur de lancement | Transformer une requête en exécution identifiable, observer son état et conserver ses reçus |
| Vérificateur | Contrôler les résultats sur critères fixés, sans accepter l'affirmation du travailleur comme preuve |
| Reçus locaux d'exécution | Preuves de processus, événements, sorties et arrêts ; ne remplacent pas les états du registre |

Un seul contrôleur possède la boucle d'une base à la fois. Il doit acquérir une exclusion locale avant lancement ; sa perte ou une impossibilité de vérifier son propriétaire bloque les nouveaux lancements. Le registre conserve ses contrôles atomiques, mais ne prouve pas à lui seul l'absence de deux contrôleurs ou de deux processus extérieurs.

Les travailleurs écrivent dans un espace propre à chaque tentative. La publication vers la sortie canonique réservée appartient au contrôleur, après vérification de la fin du travailleur et de la réservation courante. Un ancien travailleur ne doit jamais pouvoir publier directement une version tardive. La qualification initiale porte sur des programmes fixes de confiance, sans descendants ; elle ne fournit pas un sandbox pour du code arbitraire.

### Réutilisation des transitions actuelles

Le contrôleur utilisera l'API `Superviseur` ou sa CLI existante, sans écrire directement dans ses tables. Le schéma v2 et les commandes actuelles suffisent pour le premier parcours.

| Situation | Transition existante à appliquer |
|---|---|
| Tâche prête | `reserver` avant tout lancement ; récupérer `execution_id`, requête et versions d'entrées |
| Processus effectivement créé | `attacher` avec une identité réelle corrélée au reçu de lancement ; aucun identifiant inventé pour remplir le registre |
| Activité observée | `battement` sur nouvel événement observable ; ne pas le produire simplement parce que le contrôleur tourne |
| Échec sans artefact, arrêt confirmé | Conserver le constat, puis `liberer` ; le registre place la tâche en `bloquee` |
| Reprise admissible | `reprendre` avec motif, puis nouvelle `reserver` ; compteur existant conservé |
| Artefact présent et évalué | Après fin du processus, `soumettre` les observations exactes, `liberer` avec preuve de fin, puis `accepter` par le responsable prévu si tous les critères sont satisfaits |
| Entrées ou résultat périmés | `reexaminer` lorsque requis ; réexaminer les dépendants avant tout nouvel essai |

Point important du code examiné : `soumettre` exige un artefact existant et une tentative rattachée. Un échec sans fichier ne doit donc pas fabriquer un livrable vide pour satisfaire l'interface. La libération après arrêt confirmé constitue le chemin d'échec prévu. Une sortie invalide existante peut être soumise avec critères non satisfaits ; elle n'est jamais acceptée automatiquement.

Les dépendances techniques du registre relient les tâches déclarées. Elles ne surveillent pas automatiquement les fichiers sources externes à ce graphe. Le contrôleur devra figer les empreintes des entrées du scénario dans un manifeste et les vérifier avant lancement, reprise et acceptation ; une modification du CSV ne sera pas réputée détectée par le seul registre.

### Contrat de l'adaptateur proposé

Les opérations seront `launch`, `observe`, `stop`, `reconcile`, avec traduction interne en états d'observation : lancement confirmé, actif, terminé, échoué, arrêt confirmé ou inconnu. Le registre reste l'autorité sur l'état de la tâche.

Chaque reçu relie au minimum : base/mission/tâche, `execution_id`, numéro de tentative, identité réelle du processus avec élément de naissance évitant la réutilisation aveugle d'un PID, session fournisseur si disponible, empreinte de requête, espaces de travail, codes de sortie, événements et artefacts. Les paramètres appliqués et l'usage absents restent inconnus. En mode hors ligne, aucun modèle n'est déclaré exécuté, même si le préparateur a conservé un profil demandé pour compatibilité.

Le contrôleur enregistre l'intention avant de lancer, puis les reçus disponibles. Il n'existe pas de transaction atomique entre SQLite et la création d'un processus. Un crash dans cette fenêtre devient un **lancement incertain**, avec réservation conservée jusqu'à réconciliation. L'absence de reçu ne prouve pas que rien n'a démarré.

`observe` sépare processus vivant, événement reçu et progrès utile. Un silence déclenche une vérification ; il ne libère pas automatiquement la réservation. `stop` vise uniquement le processus identifié et ses éventuels descendants contrôlés. Attendre la fin du PID parent ne prouve pas la fin de descendants ; le parcours Codex devra qualifier ce point séparément. Aucun arrêt global par nom de programme.

## Premier parcours exécutable proposé

**Parcours désormais implémenté pour AUT-02A.** La recette est exécutée hors ligne avec des programmes fixes ; elle ne lance aucun modèle. Les preuves et limites sont consignées dans la réception liée ci-dessus.

```sh
python -B -m tools.supervision_locale demo \
  --scenario reprise-simple \
  --destination .orka/aut02/essai-01
```

Créer un dossier neuf, un registre v2 neuf de capacité 1 et deux mandats explicites. Le refus d'une destination existante évite de réinitialiser silencieusement compteurs ou preuves. Réutiliser le registre d'une mission réelle demanderait au contraire une commande de reprise dédiée.

### Scénario de recette hors ligne

1. **T1 : produire un total.** Nouvelles entrées fictives : `45`, `80`, `-10`, montants déjà signés. Résultat attendu par le vérificateur : JSON avec `total_net = 115`. T1 autorise au maximum deux tentatives et uniquement les fichiers de cet essai.
2. **Première tentative : échec contrôlé.** Le travailleur logiciel fixe émet un événement corrélé, puis sort avec le code 75 sans artefact ni effet extérieur. Le contrôleur observe le code, attend la fin effective et conserve le reçu. Le code 75 est un cas explicitement prévu du scénario, pas une règle de reprise applicable à tout programme.
3. **Décider la reprise.** La politique n'autorise une seconde tentative que si l'erreur est classée récupérable, le précédent rédacteur est arrêté, les versions sont valides, la délégation couvre l'action et les limites restent disponibles. Libérer, préparer la reprise motivée, puis réserver la tentative 2.
4. **Seconde tentative : produire puis contrôler.** Un nouveau processus fixe produit le JSON dans son espace. Le vérificateur recalcule depuis les entrées, contrôle le type et la valeur, puis le contrôleur publie la sortie canonique et applique soumission/libération/acceptation. Une réponse affirmant « réussi » sans ce fichier ne suffit pas.
5. **T2 dépend de T1.** Une fois T1 acceptée, produire un court bilan et les références aux preuves. Les versions d'entrées sont figées par la réservation de T2. Contrôler le bilan, accepter, puis terminer le contrôleur avec état fidèle et aucun travailleur actif.

La fonction d'acceptation est déterministe pour ce scénario. Elle éprouve la boucle de supervision, pas la compétence d'un juge IA. Les décisions ouvertes et débats restent ceux du mode portable ; leur branchement à un juge modèle appartient à une qualification ultérieure.

### Reprise du contrôleur et cas incertains

L'interface `resume` rouvre la même base à une destination explicite, sans recréer la mission. Elle vérifie d'abord le registre, l'exclusion du contrôleur, les reçus, les identités de processus et les artefacts. Un processus encore vivant n'est pas remplacé. Un processus introuvable sans preuve suffisante de fin ou d'effet reste inconnu. Le premier graphe comporte uniquement T1 et T2 dépendante ; l'ordonnancement de tâches indépendantes reste une extension.

Une réservation expirée, une fin de flux ou un fichier final présent ne valent pas preuve d'arrêt. Une interruption explicite de l'utilisateur laisse la mission suspendue : la présence d'une tâche prête n'autorise pas le redémarrage. Une coupure de machine ne déclenche pas de service de redémarrage dans ce lot.

## Adaptateur Codex ensuite

Prévoir un adaptateur optionnel autour de `codex exec`, sans installer de SDK. La commande sera construite en liste d'arguments de confiance, avec entrée standard, dossier attribué, événements JSONL, sortie structurée et identité de session explicite. Le mode exact, le modèle et les paramètres seront vérifiés au lancement ; aucune conversion silencieuse du catalogue hôte en choix CLI garanti disponible.

La première intégration se qualifie avec un faux transport CLI versionné, sans fournisseur. Une éventuelle sonde réelle exige un mandat couvrant modèle, données transmises, durée, moyens et droits, puis une vérification effective de l'environnement et des outils exposés. La connexion ChatGPT observée ne suffit pas à autoriser ou qualifier une génération. Le prototype à trois outils et ses verrous ne sont pas réutilisés en prétendant avoir déjà prouvé ces propriétés sur Codex.

Aucun contournement automatique de sandbox, de permissions ou de confiance des hooks. Ignorer une configuration personnelle ne constitue pas un confinement. Docker n'étant pas trouvé ici, son absence ne doit jamais être compensée par l'affirmation qu'un dossier de travail est un sandbox.

Le contrôleur pourra imposer nombre de lancements, tentatives et durée observée. Un plafond financier strict n'est pas promis : l'aide locale ne démontre pas une limite monétaire imposable, et un processus arrêté peut avoir engagé des coûts. L'usage retourné sera conservé lorsqu'il existe, sans montant inventé ni double comptage. Une limite obligatoire impossible à contrôler interdit les lancements qui en dépendent.

## Critères de réception figés

Ces critères ont été figés avant implémentation. Leur réception AUT-02A est maintenant détaillée dans le rapport lié en tête ; A12 concerne AUT-02B et reste non réalisé. Leur énoncé ne constitue pas à lui seul une validation.

| ID | Contrôle attendu |
|---|---|
| A01 | Le cœur du skill et son ZIP restent utilisables sans nouveau prérequis ; le superviseur est hors paquet et explicitement lancé. |
| A02 | Une réservation précède chaque lancement ; les identités enregistrées correspondent aux reçus réels. Capacité 1 et un seul contrôleur effectif dans la recette. |
| A03 | Un échec sans artefact est conservé et libéré seulement après arrêt confirmé ; aucune soumission ou acceptation fictive. |
| A04 | Le scénario nominal conserve exactement deux tentatives T1, les motifs et trois exécutions de travailleurs au total avec T2 ; aucune répétition cachée. |
| A05 | La reprise est refusée si limite atteinte, entrée périmée, autorisation manquante, ancien rédacteur actif ou effet inconnu. |
| A06 | Les sorties absentes, mauvaises valeurs, types invalides et déclarations seules ne passent pas l'acceptation. Le total 115 est recalculé par le vérificateur. |
| A07 | T2 ne démarre qu'après acceptation et validité de T1 ; modification d'une entrée ou sortie amont empêche l'acceptation aval. |
| A08 | Un crash du contrôleur aux fenêtres avant/après lancement, rattachement et publication laisse une trace récupérable et n'autorise pas un doublon par défaut. |
| A09 | Le test de silence/timeout vérifie l'identité du travailleur, son arrêt et l'absence de publication tardive ; une identité incertaine garde la réservation. |
| A10 | Une reprise utilise la même base, conserve les compteurs et respecte la suspension ; aucun daemon ou redémarrage automatique n'est annoncé. |
| A11 | Le contrôleur termine avec aucun travailleur actif pour un succès ; l'état partiel indique les preuves et branches manquantes. |
| A12 | L'adaptateur CLI refuse configuration ou contrôle incompatible, session inconnue et flux de contrôle non qualifié ; il ne reprend jamais la dernière session par simple proximité. |
| A13 | Les logs distinguent simulation, processus logiciels et appels modèles ; paramètres et coûts absents restent inconnus ; aucun secret dans les captures. |
| A14 | Les tests existants du registre restent verts ; pas de migration de schéma, modification des captures historiques, accès à L4 ou altération des prototypes. |

La première recette sera accompagnée de tests négatifs : sortie trompeuse avec code 0, code d'erreur non récupérable, compteur épuisé, travailleur silencieux, retour tardif, contrôleur interrompu et dépendance modifiée. Les essais de processus se feront dans des dossiers neufs avec programmes de confiance ; les effets extérieurs resteront simulés.

## Découpage d'implémentation proposé

| Étape | Pièces proposées | Passage |
|---|---|---|
| AUT-02A | `tools/supervision_locale/` : contrôleur, reçus, politique de reprise, adaptateur de processus fixes ; tests dédiés et nouvelles fixtures | A01–A11, A13–A14 vérifiés hors ligne sur un hôte initialement qualifié Linux |
| AUT-02B | Adaptateur Codex CLI et faux transport, sans génération réelle | Traduction des paramètres, événements et sessions qualifiée ; A12 vérifié sur transport logiciel |
| Sonde réelle optionnelle | Nouveau mandat et nouvelles preuves d'exécution | Préconditions effectives satisfaites ; aucune conclusion de qualité issue des seuls tests hors ligne |

La cible Python minimale suivra les prérequis du dépôt, mais une qualification sur Python 3.14 Linux ne démontre pas celle de Python 3.10, de Windows ou de macOS. Les contrôles dépendants des processus seront signalés par plateforme ; le cœur portable ne dépendra pas de leur présence.

## Vérification du cadrage initial et passage à AUT-02A

Le cadrage initial comprenait : lecture des transitions et tests existants ; commandes CLI d'aide/version/statut ; inventaire du Python/PATH ; deux sondes de sous-processus avec fin attendue ; documentation Context7 et officielle. À cette étape, aucun test du futur superviseur n'était exécuté. L'implémentation AUT-02A ultérieure est consignée séparément dans sa réception ; aucun agent modèle, service, sonde L4 ou nouveau prototype n'a été lancé.

Vérifications du dépôt après le cadrage seul : 90 tests réussis et 41 tests optionnels ignorés (131 recensés), paquet portable et version vérifiés. Le relevé JSON était syntaxiquement valide et le diff sans erreur. Les nouveaux résultats d'implémentation sont dans la réception AUT-02A ; ne pas attribuer les résultats du cadrage au superviseur.
