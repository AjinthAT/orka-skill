# Supervision locale persistante

Le script [superviser.py](../scripts/superviser.py) fournit un registre local de tâches, réservations et événements. Il utilise la bibliothèque standard Python et une base SQLite. Il ne lance pas de modèle, ne contacte pas de service et ne stoppe pas un agent. Le coordinateur effectue ces actions avec les outils réellement disponibles et consigne les résultats.

## Ce qui est contrôlé

- États et journal conservés dans la base après fermeture de la session.
- Dépendances directes et indirectes : chaque référence doit rester valide, avec les mêmes tentatives amont et empreintes que lors de la réservation.
- Capacité globale du registre, trois réservations actives par défaut, missions confondues.
- Réservation unique d'un fichier canonique et d'une tâche ; un même identifiant d'agent ne peut pas être rattaché à deux tentatives actives.
- Tentatives attribuées par le registre, avec un maximum par tâche, deux par défaut.
- Soumission avec observations pour chaque critère ; acceptation par le responsable nommé, seulement après libération du rédacteur et vérification de l'empreinte du résultat.
- Signalement à la demande des réservations sans activité récente, sans libération automatique.

Ces contrôles couvrent les opérations passant par cette même base. Ils ne bloquent pas un programme externe qui écrirait directement sur le disque, ni des agents lancés sans enregistrement. La preuve d'arrêt, l'identité d'agent et les paramètres appliqués sont déclarés par le coordinateur ; le script ne les vérifie pas auprès du moteur. Une preuve textuelle n'est pas un contrôle d'identité ou un dispositif de sécurité technique.

## Initialiser explicitement

Depuis la racine du projet :

```sh
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite initialiser --racine . --capacite 3
```

Le répertoire parent est créé si nécessaire. Une base existante n'est jamais remplacée. La racine des livrables est enregistrée sous forme absolue. Tous les coordinateurs qui partagent une capacité doivent utiliser la même base ; deux bases distinctes ne partagent pas leurs réservations.

## Migrer un registre existant

Depuis Orka 0.4.0, les nouvelles bases utilisent le schéma v2. L'ouverture ordinaire d'une base v1 est refusée avec une indication de migration ; elle ne la transforme pas implicitement. Arrêter les anciens coordinateurs qui utilisent le registre avant la migration. La migration ne stoppe aucun agent et ne libère aucune réservation.

```sh
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite migrer
```

La commande réserve l'écriture SQLite, crée une sauvegarde cohérente par l'API SQLite `backup` dans le même dossier (`registre.sqlite.avant-v2-<identifiant>.sqlite`), puis ajoute le champ des entrées et un événement de migration dans une transaction. La sauvegarde inclut les données validées du journal WAL. Tâches, tentatives, requêtes, empreintes, observations, événements précédents et réservations actives sont conservés. Une migration déjà faite est sans effet ; une erreur annule les changements de schéma et conserve la sauvegarde si elle a été créée. Une base absente n'est pas créée.

Les versions d'entrées historiques restent `null` : une tâche migrée ayant des dépendances n'est plus une référence valide tant qu'elle n'a pas été réexaminée et produite dans une nouvelle tentative. Les tâches sans dépendance peuvent conserver leur validité si leur fichier et les autres contrôles sont conformes. Pour une ancienne tentative active avec dépendances inconnues, vérifier et arrêter le rédacteur avant libération et reprise ; ne pas compléter rétroactivement ses entrées avec les versions actuelles.

Conserver la sauvegarde avec les précautions adaptées aux données de mission. Elle préserve la base avant migration, pas les fichiers métier ni l'état des agents. Toute restauration demande de réconcilier les exécutions et les fichiers depuis cette date ; le logiciel v1 ne lit pas le nouveau schéma v2.

Dans ce dépôt, le dossier `.orka/` est ignoré par Git, car les requêtes et leur contexte peuvent contenir des informations de mission. Après installation dans un autre projet, ajouter la règle correspondante à son fichier d'exclusion ou stocker la base hors du dépôt ; l'installateur ne modifie pas les règles Git du projet hôte. Ce choix ne chiffre pas la base et ne constitue pas une sauvegarde. Aucune base de mission réelle n'a été créée pendant le développement ; les tests utilisent des dossiers temporaires.

## Enregistrer puis réserver

Le mandat suit [le contrat JSON](prompting-agents.md). Pour ce registre, `sortie` doit désigner un fichier local sous la racine choisie et correspondre au paramètre `--fichier`. Un simple résultat conversationnel reste utilisable avec le préparateur seul.

Exemple de forme de commande, avec un mandat réel préparé par le coordinateur :

```sh
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite ajouter --mandat chemin/mandat.json --fichier projets/mon-projet/livrables/T-001.md --maximum 2
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite reserver --mission mon-projet --tache T-001
```

Les chemins et identifiants sont à adapter ; les exemples ne désignent pas des missions existantes. Ajouter les dépendances avec `--dependance T-001`. Elles doivent déjà être enregistrées dans la même mission ; ajouter les tâches dans l'ordre de leurs dépendances. Cette version ne modifie pas un graphe existant et refuse les références futures ou à soi-même, ce qui empêche de créer un cycle par l'interface proposée.

Le registre fige le prompt, le profil et les paramètres au moment de l'ajout. Une réservation ou une reprise ne recharge pas silencieusement un nouveau catalogue. Modifier le mandat ou les dépendances d'une tâche enregistrée demande pour l'instant une nouvelle tâche avec un identifiant distinct et une analyse d'impact ; aucune commande de modification ou de suppression n'est fournie.

Une reprise conserve cette base et ajoute le motif enregistré et les observations précédentes au contexte de la nouvelle tentative. Son empreinte de prompt et celle de la requête sont recalculées ; le modèle et l'effort restent inchangés. Une nouvelle tentative ne répète donc pas silencieusement le prompt sans le constat à traiter.

La réservation produit un `execution_id`, la phase `reservee` et la requête de lancement. Les critères y figurent avec les identifiants C-01, C-02, etc. La place et le fichier sont réservés mais aucun agent n'est encore lancé.

Elle conserve aussi, pour chaque dépendance enregistrée, l'identifiant de la tentative amont et l'empreinte de son résultat. Ces données figurent dans `entrees_verifiees` de la requête et dans le prompt transmis. Il s'agit des versions déclarées à utiliser, pas d'une preuve que l'agent les a effectivement lues. Les sources externes et fichiers qui ne sont pas déclarés comme dépendances ne sont pas surveillés automatiquement.

## Raccorder une exécution réelle

1. Vérifier les capacités, le mandat et les limites encore applicables, puis réserver la tâche.
2. Transmettre la requête au lanceur de sous-agents compatible.
3. Rattacher l'identifiant effectivement retourné avec `attacher --execution IDENTIFIANT --agent AGENT`. `--appliques chemin/reglages.json` est facultatif et attend `model` et `reasoning_effort` lorsqu'ils ont été observés. Sans information, les laisser inconnus.
4. Enregistrer une activité confirmée avec `battement --execution IDENTIFIANT` lorsque nécessaire. Ne pas fabriquer des battements si l'état de l'agent n'est pas connu.
5. À réception, vérifier le fichier et consigner les observations avec `soumettre --execution IDENTIFIANT --observations chemin/observations.json`.
6. Après confirmation que le rédacteur ne peut plus écrire, utiliser `liberer --execution IDENTIFIANT --preuve-arret "référence du constat"`.
7. Le responsable désigné peut utiliser `accepter --mission mon-projet --tache T-001 --validateur coordinateur` après sa revue. Tous les critères sont indispensables dans cette première version du registre.

Un fichier d'observations associe exactement chaque identifiant de critère à `etat` et `preuve`. Les états sont `satisfait`, `non_satisfait` ou `non_verifie`. Le script exige une preuve ou un constat non vide et contrôle le fichier et son empreinte ; il ne juge pas la justesse métier du texte de preuve.

Si le lancement échoue avec certitude avant création de l'agent, consigner ce constat puis libérer la réservation. Si le résultat du lancement est incertain, conserver la réservation jusqu'à vérification ; ne pas créer aveuglément un second agent.

## Interruption, reprise et alertes

`etat` affiche tâches, réservations, paramètres demandés ou déclarés, `entrees_utilisees` et `entrees_a_reexaminer`. Il distingue l'état documentaire enregistré (`etat`) de la validité actuelle (`validite`) : une tâche acceptée peut rester historiquement `terminee` mais avoir une validité `a_reexaminer`. `dependances_a_reexaminer` indique les références amont actuellement invalides ; les entrées figées peuvent aussi être périmées après une nouvelle validation amont. Cette lecture ne modifie ni états ni réservations. `journal` expose les événements. `alertes --delai 300` signale les réservations sans activité depuis au moins 300 secondes ; le délai est fourni par l'opérateur. Ce signal ne prouve pas qu'un agent est arrêté.

Pour analyser qualité, reprises et moyens connus, constituer le relevé du [bilan local des agents](bilan-agents.md) à partir des tentatives réellement rattachées et des compteurs disponibles. Ce bilan est un outil séparé ; aucune collecte ni export automatique depuis SQLite n'est ajouté au registre.

Après réouverture de la base, les réservations restent actives. Vérifier les agents concernés avant de les libérer. Une libération sans résultat laisse la tâche bloquée. Une tâche bloquée ou à corriger peut passer par `reprendre --mission ... --tache ... --motif "constat"` après libération. Le compteur de tentatives n'est pas remis à zéro.

Si la réponse d'une réservation a été perdue, retrouver son identifiant dans `etat`, puis utiliser `requete --execution IDENTIFIANT` pour récupérer la requête enregistrée. Examiner sa phase, son activité et l'agent rattaché avant toute action ; cette lecture n'autorise pas à relancer une tentative déjà lancée. Ne pas créer une nouvelle réservation pour remplacer un résultat de lancement encore incertain.

Le résultat soumis garde sa réservation jusqu'à la libération explicite. L'acceptation contrôle l'empreinte à cet instant et refuse un résultat ou une dépendance modifiés depuis la version vérifiée. La base conserve les empreintes et observations, pas une copie de sauvegarde des livrables.

## Réexaminer un résultat terminé

Un changement de source invalide ses résultats dépendants transitivement. Une nouvelle acceptation de la source ne rétablit pas les anciens résultats dépendants : leurs versions d'entrées restent celles de leur tentative. Cela s'applique même si deux tentatives amont ont produit les mêmes octets.

```sh
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite reexaminer --mission mon-projet --tache T-001 --motif "Source ou conclusion à vérifier" --validateur coordinateur
python3 .agents/skills/orka/scripts/superviser.py --base .orka/registre.sqlite reprendre --mission mon-projet --tache T-001 --motif "Traiter le réexamen"
```

`reexaminer` exige une tâche terminée, un motif, le responsable d'acceptation nommé et l'absence de réservation active sur son fichier. Il passe la tâche à `a_reexaminer`, conserve les acceptations et preuves anciennes, journalise le motif et retourne les identifiants des dépendants à examiner. Ceux-ci ne sont ni relancés ni libérés ni réécrits automatiquement ; leurs états actifs sont conservés, et leur acceptation reste soumise à la validité des entrées.

`reprendre` prépare ensuite une nouvelle tentative selon les contrôles existants. La réservation fige les nouvelles versions seulement lorsque les dépendances sont valides. Les compteurs et maximums ne sont jamais remis à zéro ; un réexamen peut être enregistré même si aucune tentative supplémentaire n'est disponible. Une tâche de remplacement exige alors un nouvel identifiant et une analyse d'impact, pas le contournement silencieux de la limite.

Les fichiers peuvent être modifiés par des programmes extérieurs pendant ou après ces contrôles : le registre ne les verrouille pas. Une version déjà invalide ne peut pas être acceptée par les contrôles du registre ; cela ne garantit pas une surveillance continue du système de fichiers.

## Limites de ce jalon

Le registre impose capacité, dépendances, réservations, transitions et tentatives dans son propre périmètre. Il ne fournit pas encore de service continu, d'alertes envoyées automatiquement, de plafond de coût financier, de contrôle technique des outils, de lancement automatique ni de reprise automatique d'un processus interrompu.

Les réservations SQLite sont atomiques entre les processus qui utilisent le registre. Elles ne constituent pas des verrous du système de fichiers. La base doit rester accessible à un usage local adapté ; aucune synchronisation distribuée ni garantie sur un stockage réseau n'est fournie.
