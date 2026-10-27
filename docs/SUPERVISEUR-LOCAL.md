# Superviseur facultatif AUT-02A

Propriétaire : coordinateur de maintenance. Version documentaire : 3, 27 octobre 2026. Périmètre : recette logicielle hors ligne du dépôt, qualifiée initialement sur Linux/Python 3.14, avec corrections de reprise, d'arrêt et de suspension pendant le nettoyage. Le [lot AUT-02](LOT-AUT-02.md) définit les critères ; la [réception](VALIDATION-AUT-02A.md) précise les preuves et limites.

## Exécuter le premier parcours

Depuis la racine d'un clone du dépôt, sur Linux avec Python 3.10+ et `/proc` :

```sh
python -B -m tools.supervision_locale demo \
  --scenario reprise-simple \
  --destination .orka/aut02/essai-01
```

Choisir une destination neuve. La commande refuse de remplacer un dossier existant. Elle crée un registre v2 de capacité 1, les données fictives `45, 80, -10`, deux mandats et les reçus. Le superviseur ne fait partie ni du ZIP ni de l'installation du skill ; aucun paquet tiers, SDK, CLI fournisseur ou modèle n'est utilisé.

T1 échoue une fois avec le code 75, termine, puis est libérée et reprise avec un motif conservé dans le registre. La seconde tentative produit `sorties/total.json` contenant `{"total_net": 115}`. Le contrôleur recalcule ce résultat avant de le publier et de l'accepter. T2 dépend de cette version acceptée et produit `sorties/bilan.json`. Le parcours nominal comporte exactement trois processus de travailleurs et se termine sans travailleur actif.

La sortie de la commande est un JSON. Code de sortie `0` : succès vérifié du parcours, ou commande d'état/suspension exécutée. Code `2` : parcours partiel ou commande refusée ; lire `motif` et le registre. Le succès d'une commande d'état ne signifie pas que la mission est terminée.

## État, interruption et reprise

```sh
python -B -m tools.supervision_locale etat --destination .orka/aut02/essai-01
python -B -m tools.supervision_locale resume --destination .orka/aut02/essai-01
```

`resume` rouvre la même base, sans remettre les compteurs à zéro. Il réconcilie les réservations avec les reçus et les identités Linux (PID, naissance noyau et démarrage machine). Un travailleur encore actif est attendu, puis arrêté à son échéance si un arrêt ciblé est possible. Après perte du parent, l'arrêt ciblé utilise `pidfd` lorsqu'il est disponible ; sinon l'état reste partiel. Un PID seul ou un délai expiré ne vaut pas preuve d'arrêt.

L'échéance monotone est rattachée au démarrage machine dans chaque requête. Si ce démarrage diffère, ou n'est pas déclaré, aucune comparaison temporelle, attente d'ancien lancement ou nouvelle exécution n'est autorisée : la réservation reste conservée et l'état est partiel. Une ancienne mission dont le code a changé reste soumise à la requalification déjà prévue ; ces corrections ne migrent pas silencieusement ses preuves.

`Ctrl+C` suspend la mission et conserve les réservations, y compris si l'ouverture du registre est interrompue après acquisition du verrou du contrôleur. Dans ce cas, le JSON retourne `registre: null` car aucun état du registre n'a pu être lu ; la suspension persiste dans `controle.json`. Les enfants possédés font l'objet d'une tentative d'arrêt bornée. La commande de suspension ci-dessous s'utilise entre deux exécutions du contrôleur ; pendant une exécution, utiliser `Ctrl+C`. Aucun service ne redémarre automatiquement.

Si la fin d'un enfant ne peut pas être confirmée après les signaux et attentes bornées, le contrôleur retourne un état partiel avec `arrets_non_confirmes`. Aucun reçu d'arrêt n'est fabriqué et aucune réservation n'est libérée sur cette seule tentative d'arrêt. Un nettoyage incomplet interdit le succès, même si les tâches ont déjà été acceptées dans le registre.

Un premier `Ctrl+C` reçu pendant le nettoyage, y compris pendant la fermeture du registre, est mémorisé sans interrompre les opérations d'arrêt bornées. La suspension est ensuite persistée et le JSON final reste partiel. Les signaux répétés pendant cette phase ne recommencent pas les attentes. Dans le thread principal, le gestionnaire de `SIGINT` est remplacé uniquement pendant la finalisation, puis rétabli ; il ne fait aucune écriture depuis le signal lui-même. Le contrôle des réservations reste inchangé.

```sh
python -B -m tools.supervision_locale suspendre --destination .orka/aut02/essai-01
python -B -m tools.supervision_locale resume \
  --destination .orka/aut02/essai-01 --reprendre-suspension
```

Une reprise normale respecte la suspension. Le dernier indicateur est une instruction explicite pour la lever ; il ne lève aucune autre restriction. Une erreur permanente, un timeout, un résultat invalide ou une entrée modifiée ne déclenche pas une nouvelle tentative automatique.

Un crash entre réservation et preuve de création peut laisser un lancement incertain. Dans ce cas, la réservation reste active et aucune répétition n'est lancée. La version initiale ne fournit pas de commande `force`, de remise à zéro ou de résolution manuelle automatique : examiner les preuves avant toute intervention. Modifier les reçus pour débloquer la mission ne constitue pas une confirmation d'arrêt.

## Refaire les cas négatifs

Chaque cas nécessite une destination différente. Exemple :

```sh
python -B -m tools.supervision_locale demo \
  --scenario reprise-simple --destination .orka/aut02/erreur-01 \
  --incident mauvais-total
```

| Option | Effet du programme fixe |
|---|---|
| `--incident erreur-permanente` | Code 65, sans reprise |
| `--incident epuisement` | Code 75 jusqu'à épuisement des deux tentatives |
| `--incident sortie-absente` | Code 0 mais aucun livrable : refus |
| `--incident mauvais-total` ou `mauvais-type` | JSON incorrect : refus |
| `--incident silence` | Travailleur silencieux, arrêté après l'échéance |
| `--incident retour-tardif` | Production retardée d'une seconde ; utiliser `--delai 0.2` pour provoquer le timeout |
| `--sans-reprise` | Aucun second essai autorisé après le premier code 75 |
| `--maximum-t1 1` | Une seule tentative permise |
| `--delai N` | Échéance par travailleur, entre 0.1 et 30 secondes ; défaut 2 |

Ce sont des programmes de recette fixes, sans descendants. Les échecs n'entraînent pas l'exécution d'une commande arbitraire fournie par l'utilisateur.

## Où lire les preuves

| Chemin sous la destination | Fonction |
|---|---|
| `registre.sqlite` | Autorité sur tâches, dépendances, réservations, compteurs, soumissions et acceptations |
| `mission.json`, `mission.sha256` | Mandat de recette, politique de reprise, empreintes des entrées, des mandats et du code examiné |
| `controle.json` | Suspension explicite ; aucun état de tâche dupliqué |
| `controleur.lock` | Exclusion locale par `flock`, jamais déverrouillée par suppression du fichier |
| `controleur.jsonl` | Intentions de lancement, décisions et constats ; un journal tronqué bloque la reprise |
| `executions/<id>/requete.json` | Corrélation avec la requête réservée, entrée figée, numéro, échéance monotone et démarrage machine associé |
| `executions/<id>/demarre.json`, `termine.json` | Reçus du programme fixe ; une fin déclarée doit être corroborée par l'arrêt de sa naissance Linux |
| `executions/<id>/arret.json` | Preuve de fin recueillie par le contrôleur, avec sa provenance |
| `executions/<id>/resultat.json` | Sortie de tentative, conservée même si incorrecte ; aucun accès direct du travailleur à la publication canonique |
| `sorties/` | Résultats publiés par le contrôleur après arrêt et vérification |

Les reçus utilisent des remplacements atomiques et synchronisations de fichiers/dossiers. La création d'un processus et SQLite ne forment pas une transaction commune ; l'incertitude est conservée. Le contrôleur refuse de reprendre si les empreintes du code, du mandat ou des sources ont changé. Une telle modification exige une requalification ; la suppression des empreintes ne la remplace pas.

## Limites

AUT-02A contrôle des programmes fixes de confiance, dans un dossier local de confiance. Il ne constitue pas un sandbox pour du code hostile, une garantie contre un autre programme qui contourne le verrou ou modifie les fichiers, ni une sauvegarde. Les gardes de chemins refusent les déplacements et liens symboliques observés, sans garantir le confinement face à un attaquant concurrent. `flock` et la durabilité ne sont qualifiés ici que sur stockage local Linux, pas sur un partage réseau.

Le contrôleur utilise une fonction d'acceptation déterministe ; aucun juge IA n'est exécuté. Le profil Codex demandé dans le registre existe pour compatibilité avec le préparateur, mais les paramètres appliqués restent inconnus et `appels_modeles` vaut zéro. Aucune amélioration de qualité d'une IA, consommation ou économie financière n'est déduite de ces tests.

Le noyau portable du skill reste inchangé en 0.9.0. L'adaptateur Codex CLI, les appels modèles, le redémarrage automatique, les descendants arbitraires, d'autres plateformes et les limites financières sont hors AUT-02A.

## Validation locale

```sh
python -B -m unittest discover -s tests -p test_supervision_locale.py -v
python -B tools/verifier.py
```

Les tests créent leurs essais dans des dossiers temporaires et ne rejouent pas les captures historiques. Ils incluent des crashs réels du contrôleur par `os._exit`, un `SIGINT`, des travailleurs réels et des variantes logicielles négatives. Les tests Linux sont explicitement ignorés sur les autres systèmes ; cela ne constitue pas une qualification de ces systèmes.
