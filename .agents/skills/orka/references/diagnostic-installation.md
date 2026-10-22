# Vérifier une installation Orka

Le diagnostic est facultatif et en lecture seule. Il examine un dossier explicitement indiqué ; il ne répare rien, ne lance aucun modèle et ne modifie pas les paramètres de l'assistant. Les rôles et workflows restent utilisables sans Python.

## Contrôle manuel, sans Python

1. Dans le dossier de skills configuré pour votre assistant, ouvrez le dossier `orka` complet, pas seulement `SKILL.md`. Un chemin personnalisé est possible : utilisez votre configuration connue plutôt que de déplacer les fichiers au hasard.
2. Vérifiez la présence de `SKILL.md`, `GUIDE.md`, `GUIDE.fr.md`, `LICENSE`, des références et des scripts de l'archive téléchargée. Dans `SKILL.md`, le début déclare `name: orka`, une description, `license: MIT` et `metadata.version`. La version affichée est une déclaration du fichier.
3. Ouvrez les guides puis quelques références utiles par leurs liens locaux. Si une ressource manque, comparez le dossier avec une extraction complète d'une release connue. Sauvegardez les adaptations avant tout remplacement ; conserver la licence et tout le dossier accompagne l'installation manuelle.
4. Dans une nouvelle session de l'assistant, vérifiez séparément que vous pouvez sélectionner Orka et lui demander d'afficher son guide. La présence des fichiers ne prouve ni leur chargement, ni l'accès au Web ou aux sous-agents. Si l'hôte ne le reconnaît pas, relevez le chemin choisi, la version déclarée et le message exact avant d'examiner la configuration adaptée à cet hôte.

Ce contrôle manuel ne compare pas automatiquement les empreintes et ne prouve pas l'identité intégrale avec une release.

## Outil facultatif, Python 3.10+

Exécutez une copie du [diagnostic](../scripts/diagnostiquer.py) dont vous connaissez la provenance. Depuis la racine d'un dépôt Orka examiné :

```sh
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /chemin/du/skill/orka
```

Ou utilisez le script d'une installation connue, en adaptant son chemin. Le dossier à examiner peut être une autre installation ; son code ne sera pas importé ni exécuté. Il n'est pas nécessaire d'avoir cloné le dépôt pour utiliser la copie du diagnostic incluse dans le ZIP du skill. L'outil exige un chemin explicite et n'inventorie pas vos autres installations.

Pour comparer avec une référence connue extraite dans un autre dossier et obtenir un rapport JSON :

```sh
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /chemin/du/skill/orka --reference /chemin/reference/orka --json
```

La référence doit être le dossier `orka` complet, licence comprise, pas la racine du dépôt source. Son authenticité reste à établir par votre provenance de téléchargement ; le diagnostic compare les octets fournis. Une différence peut être une adaptation volontaire ou une autre version. Le rapport propose de l'examiner, sans écraser de fichier. Sans référence valide et inventaires complets, l'intégrité reste `non_verifiee`.

| Résultat | Lecture |
|---|---|
| Code 0 | Aucune anomalie détectée dans les contrôles effectués ; les éléments non vérifiés restent visibles |
| Code 1 | Dossier ou métadonnées non lisibles, ressource manquante, lien invalide, inspection incomplète ou différence avec la référence |
| Code 2 | Arguments de commande invalides |
| `activation_hote: non_verifiee` | Aucun assistant lancé pour vérifier la découverte du skill |
| `capacites_hote: non_verifiees` | Modèles, outils et délégation non interrogés |

Le JSON version 1 contient installation, référence éventuelle, inventaires SHA-256, complétude de lecture, constats (`id`, `etat`, `preuve`, `action`), résumé et code de sortie. Ce rapport est local ; vérifiez ses chemins et son contenu avant de le publier. Il ne contient pas de relevé de consommation.

## Formats et limites de lecture

- Métadonnées : frontmatter délimité par `---`, scalaires textuels sur une ligne et mapping `metadata` indenté de deux espaces ; `version` au format `x.y.z`. Les chaînes peuvent être simples avec apostrophes doublées, doubles avec échappements JSON ou simples non citées sans syntaxe YAML spéciale. Les commentaires sur leur propre ligne sont acceptés. Listes, ancres YAML, commentaires en fin de valeur et blocs multilignes ne sont pas pris en charge et sont signalés ; un tel constat ne signifie pas que tout YAML de cette forme est invalide pour l'hôte.
- Liens : liens/images Markdown directs, définitions de références et attributs HTML `href`/`src` ; exemples en blocs de code ignorés. Les cibles locales et ancres de titres Markdown sont contrôlées. Ce n'est pas un parseur Markdown complet ni une vérification de rendu dans le navigateur.
- Aucun lien externe n'est ouvert. Les chemins absolus et sortants sont signalés. Les liens symboliques et points de réanalyse, y compris les jonctions Windows, ne sont pas suivis, même s'ils pointent à l'intérieur. Les fichiers spéciaux ne sont pas lus. Le chemin racine choisi est résolu explicitement avant l'inspection.
- `.DS_Store`, `__pycache__` et les fichiers `.pyc` sont exclus des inventaires ; ce sont les mêmes exclusions de distribution que l'installateur. Le texte UTF-8 est limité à 1 Mio par document ; les autres fichiers sont hachés par blocs sans exécution.
- L'outil vérifie les chemins avant ouverture et l'identité du fichier ouvert. Il ne fournit pas une sandbox ni une garantie de cohérence contre des modifications concurrentes du système de fichiers. Pour une comparaison stable, examinez des copies qui ne sont pas en cours d'édition.

Le diagnostic ne nécessite aucun paquet tiers et n'ajoute ni réseau, hook, collecte de sessions, service permanent ou réparation automatique. Une inspection réussie n'est pas une certification de sécurité du code contenu dans le dossier.
