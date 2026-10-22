# Parcours de découverte D1

## Verdict

Le parcours permet de préparer une première mission : le README fournit une installation manuelle compréhensible, les guides précisent le démarrage et le ZIP public se télécharge puis s’extrait avec le dossier attendu. Aucun blocage documentaire ou de téléchargement n’a été observé sur cette route. L’activation dans une nouvelle session et l’exécution d’une mission ne sont pas validées et n’ont pas été tentées.

## Étapes et preuves

1. Lecture intégrale de `README.md`, seul point d’entrée. Enregistrement de `premier-regard.md` avant toute ouverture d’un lien ; ce fichier n’a pas été réécrit. Le texte définit Orka comme un « Agent Skill » et distingue les sous-agents des perspectives successives. Il donne directement `~/.agents/skills/orka/` et `$orka` pour Codex, un exemple de mission, et précise « You can install and use Orka without Python. » Ces informations suffisent déjà à choisir le parcours et à formuler une demande.
2. Lecture de `docs/INSTALLATION.md`, par son lien dans le README. La route « Without Python: copy the skill folder » confirme la copie complète ; elle indique explicitement que les scripts inclus ne sont pas exécutés par cette opération. La mention du dossier de l’hôte configuré et de la nouvelle session couvre les variantes sans prétendre garantir leur détection. Aucune route Python n’a été exécutée.
3. Lecture de `.agents/skills/orka/GUIDE.fr.md`, par le lien « Français » du tableau Documentation. Le guide précise les informations utiles : projet, résultat, dossier, contraintes. Il propose plusieurs premiers messages selon le besoin et indique qu’une idée encore floue suffit au cadrage. Le français et ces exemples sont un complément de confort ; ils ne débloquent pas un obstacle rencontré dans le README.
4. Téléchargement de [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip), lien présent dans le README et le guide d’installation. La redirection passe par `/releases/download/v0.4.1/orka.zip` puis un lien temporaire de GitHub Release Assets. Réponse finale HTTP 200, 113 185 octets reçus ; pas d’erreur. En-têtes conservés dans `zip-http-headers.txt`. Empreinte SHA-256 : `dd00213bce58409518c4d1204cfd1872ef6334c03117c239bda301380cc31ede`.
5. Inspection de la liste du ZIP puis extraction sous `installation-demo/`, sans exécuter son contenu. Les 41 entrées deviennent 41 fichiers, sous une seule racine `orka`. Les fichiers `orka/SKILL.md`, `orka/GUIDE.md`, `orka/GUIDE.fr.md` et `orka/LICENSE` sont présents. Le manifeste complet est enregistré dans `archive-manifest.json`, et la liste absolue des fichiers créés dans `trace.json`. La lecture des 32 premières lignes de `installation-demo/orka/SKILL.md` confirme `name: orka`, la version `0.4.1`, les liens relatifs vers les guides et le démarrage. Il s’agit d’une lecture documentaire, pas d’une activation du skill.
6. Préparation du message ci-dessous, sans l’envoyer ni commencer l’étude. L’extraction constitue la copie de démonstration demandée ; aucune copie dans un répertoire personnel de skills n’a été réalisée.

## Premier message prêt à copier

```text
$orka
Étudie un produit de prise de rendez-vous pour les coachs sportifs indépendants en France. Évalue les besoins clients, les alternatives et concurrents, la faisabilité technique et les hypothèses de prix. Utilise les spécialistes utiles si la délégation est disponible et autorisée. Enregistre une synthèse de décision en français dans projets/reservation-coachs-france/, avec sources datées, incertitudes et prochain test de validation proportionné. Distingue faits vérifiés et hypothèses. Cette demande porte sur l’étude ; toute réalisation ultérieure sera décidée à partir de ses résultats.
```

## Constats, conséquences et prochaines actions

| Constat | Conséquence dans ce test | Prochaine action possible |
|---|---|---|
| Le README donne le chemin, l’invocation et un exemple concret. | Préparer une première mission est possible dès le premier fichier. | Copier le message dans une session où Orka est installé. |
| Les guides liés sont accessibles et cohérents sur la route manuelle choisie. | Aucun complément hors dépôt n’a été nécessaire. | Les consulter au besoin, sans lecture exhaustive des références. |
| Le ZIP public fonctionne et contient la racine attendue ainsi que les guides. | La démonstration d’extraction est réussie. | Pour une installation réelle autorisée, copier le dossier complet dans le répertoire configuré et sauvegarder une éventuelle version existante. |
| La cible « latest » est une release 0.4.1, indépendamment de la copie documentaire figée. | Le téléchargement prouve la disponibilité de cette release, pas son identité intégrale avec le commit fourni. | Épingler une release précise si une reproduction future doit employer exactement les mêmes octets. |
| Détection du skill, accès aux outils et délégation dépendent de l’hôte. | Ni leur réussite ni leur échec n’ont été observés. | Dans le cadre d’un autre essai autorisé, ouvrir une nouvelle session et vérifier la sélection d’Orka. |
| Langue anglaise du README et instructions détaillées en français annoncées. | Pas de blocage pour cette lecture ; préférence de présentation uniquement. | Utiliser les traductions liées selon la langue souhaitée. |

## Limites et périmètre

Un passage unique, sans correction du dépôt ni consultation des résultats d’autres agents. Les seuls documents de la copie publique lus sont `README.md`, `docs/INSTALLATION.md` et `.agents/skills/orka/GUIDE.fr.md`. L’image de bannière, les résultats d’évaluation, les autres guides, les références et les sites des hôtes n’ont pas été ouverts. Le téléchargement a nécessairement suivi les redirections publiques du lien ZIP ; aucune recherche générale, authentification ou action externe de publication n’a eu lieu.

Hors copie publique, j’ai lu le mandat fourni puis le début du `SKILL.md` du ZIP téléchargé dans l’installation de démonstration. Ces lectures sont consignées. Aucun skill personnel n’a été lu pour compléter le parcours ; aucun script livré n’a été exécuté. Le contexte hérité de l’assistant existe, mais je n’ai pas consulté la conversation principale ni utilisé d’autres dépôts pour combler une information manquante.

Mesures accessibles : code HTTP, taille téléchargée, empreinte du ZIP, noms et nombre d’entrées/fichiers, présence des fichiers attendus et version déclarée. Aucun jeton, coût, avantage qualité, efficacité commerciale, comportement d’une mission ou activation réelle n’est mesuré. Le commit fourni par le mandat sert d’identifiant de la copie ; son historique Git n’a pas été inspecté.
