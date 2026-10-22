# Installation

[Retour à Orka](../README.fr.md) · [English](INSTALLATION.md)

## Sans Python : copier le dossier du skill

1. Téléchargez [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) et décompressez-le. Utilisez le ZIP du skill, pas l'archive du dépôt complet.
2. Copiez tout le dossier `orka` extrait, avec ses références et guides, dans le dossier de skills de votre assistant. Emplacements utilisateur par défaut : `~/.agents/skills/orka/` pour Codex, `~/.claude/skills/orka/` pour Claude Code ou `~/.hermes/skills/orka/` pour le profil Hermes par défaut. Adaptez-les à votre configuration et sauvegardez une installation existante avant remplacement.
3. Ouvrez une nouvelle session si nécessaire, sélectionnez Orka et donnez une mission. Pour Claude Web/ordinateur, importez le ZIP dans l'interface des skills personnalisés plutôt que de copier un dossier local.

Ces étapes n'exécutent aucun script Python fourni. Les fichiers facultatifs peuvent rester présents sans être utilisés.

## Installateur Python facultatif : Codex ou Claude Code

Téléchargez et décompressez le [code source](https://github.com/AjinthAT/orka-skill/archive/refs/heads/main.zip), ou clonez le dépôt :

```sh
git clone https://github.com/AjinthAT/orka-skill.git
cd orka-skill
```

Avec Python 3.10 ou plus récent, choisissez la commande correspondant à votre assistant :

```sh
# Codex : installation pour votre utilisateur
python3 install.py --agent codex

# Claude Code : installation pour votre utilisateur
python3 install.py --agent claude
```

Sous Windows, utilisez `py -3` si `python3` n'est pas disponible. Aucun paquet Python tiers n'est nécessaire.

| Assistant | Pour votre utilisateur | Pour un projet |
|---|---|---|
| Codex | `~/.agents/skills/orka/` | `<projet>/.agents/skills/orka/` |
| Claude Code | `~/.claude/skills/orka/` | `<projet>/.claude/skills/orka/` |

Pour limiter l'installation à un projet existant, ajoutez `--project /chemin/du/projet`. Sans cette option, l'installation concerne votre utilisateur.

L'installateur copie le dossier complet, la licence et les deux guides de démarrage, puis affiche leurs chemins et un premier message suggéré. Il fonctionne sans appel réseau ni modification de vos paramètres et refuse d'écraser un dossier existant. Ouvrez une nouvelle session si nécessaire, puis utilisez `$orka` dans Codex ou `/orka` dans Claude Code. Les imports ZIP contiennent aussi les guides ; leur ouverture automatique dépend de l'application.

## Claude sur le Web ou sur ordinateur

Téléchargez [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip), puis importez cette archive dans l'interface des skills personnalisés de Claude et activez-la. Utilisez l'archive du skill, et non celle du dépôt complet. La disponibilité dépend de votre compte et des paramètres de votre organisation : consultez le [guide officiel Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

L'import ne donne pas accès à vos fichiers locaux et n'active pas de sous-agents parallèles. Les outils et le stockage restent ceux de l'application hôte.

## Hermes Agent

La copie manuelle décrite plus haut convient aussi au profil Hermes par défaut. Si vous préférez l'installateur Python facultatif, lancez depuis le dépôt cloné :

```sh
python3 install.py --destination "$HOME/.hermes/skills/orka"
```

Ouvrez une nouvelle session, puis utilisez `/orka`. Pour un autre profil ou `HERMES_HOME`, indiquez son dossier `skills/orka` avec `--destination`. Ce chemin suit la [documentation Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) ; une mission Orka complète dans Hermes n'a pas encore été testée.

## Autres assistants

Le dossier suit le [format ouvert Agent Skills](https://agentskills.io/specification). Copiez l'intégralité de `.agents/skills/orka/` dans le répertoire documenté par votre application, ou indiquez une destination exacte :

```sh
python3 install.py --destination /chemin/des/skills/orka
```

Un modèle seul ne suffit pas : l'application qui l'utilise doit prendre en charge les skills ou pouvoir lire ces fichiers et leurs références. Sans prise en charge native, vous pouvez fournir les fichiers manuellement ; leur découverte automatique n'est pas disponible. La compatibilité avec toutes les applications IA n'est pas garantie.

## Mise à jour et désinstallation

### Vérifier l'installation avant remplacement

Sans Python, ouvrez le dossier `orka` configuré et vérifiez `SKILL.md`, les deux guides, la licence et les ressources de l'archive. Essayez les liens locaux, puis vérifiez séparément la sélection du skill dans une nouvelle session de l'hôte. En cas de manque, comparez avec une extraction complète connue et préservez les adaptations avant remplacement.

Le [diagnostic facultatif](../.agents/skills/orka/scripts/diagnostiquer.py), disponible depuis 0.5.0, exige Python 3.10+ et fonctionne en lecture seule. Depuis la racine d'un dépôt examiné :

```sh
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /chemin/du/skill/orka
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /chemin/du/skill/orka --reference /chemin/reference/orka --json
```

Adaptez le chemin du script si vous utilisez sa copie installée. Il ne répare rien, n'ouvre pas le réseau et ne lance pas l'assistant. Codes : 0 sans anomalie détectée dans les contrôles effectués, 1 en cas d'anomalie ou de différence, 2 pour des arguments invalides. Sans référence complète valide, l'intégrité reste non vérifiée ; une concordance ne prouve pas l'authenticité de la référence. Activation, modèles, outils et délégation restent non vérifiés. La [procédure détaillée](../.agents/skills/orka/references/diagnostic-installation.md) précise les formats pris en charge et les limites.

Sauvegardez vos adaptations avant de remplacer un dossier `orka` existant. L’installateur fourni refuse de l’écraser. Pour désinstaller, supprimez uniquement le dossier du skill installé ; conservez vos livrables de mission. Les guides sont inclus dans le ZIP, mais leur ouverture automatique dépend de l’assistant.

Références de format et d’hôtes : [Agent Skills](https://agentskills.io/specification), [OpenAI](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills).
