# Orka

**Une équipe d'entreprise coordonnée dans votre assistant IA.**

[English](README.md) · [Télécharger Orka](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) · [Instructions du skill](.agents/skills/orka/SKILL.md)

Orka est un skill au format Agent Skills : un coordinateur mobilise les spécialistes utiles à votre mission, organise leurs échanges, vérifie les preuves et consolide les livrables. Il couvre stratégie, étude de marché, marketing, commercial, produit, développement, qualité, exploitation, finance, RH et relation client.

**28 rôles · 8 équipes · 9 workflows · Licence MIT**

Le dépôt fournit les instructions, modèles de documents et outils Python facultatifs. Votre assistant fournit les modèles et les outils d'exécution. L'installation ne lance aucun agent, ne crée aucun service et ne nécessite aucune clé API. L'utilisation des modèles dépend de votre assistant, de votre abonnement et des coûts associés.

## Installation

### Codex ou Claude Code

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

L'installateur copie le dossier complet et la licence, sans appel réseau ni modification de vos paramètres. Il refuse d'écraser un dossier existant. Ouvrez une nouvelle session si nécessaire, puis utilisez `$orka` dans Codex ou `/orka` dans Claude Code.

### Claude sur le Web ou sur ordinateur

Téléchargez [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip), puis importez cette archive dans l'interface des skills personnalisés de Claude et activez-la. Utilisez l'archive du skill, et non celle du dépôt complet. La disponibilité dépend de votre compte et des paramètres de votre organisation : consultez le [guide officiel Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

L'import ne donne pas accès à vos fichiers locaux et n'active pas de sous-agents parallèles. Les outils et le stockage restent ceux de l'application hôte.

### Autres assistants

Le dossier suit le [format ouvert Agent Skills](https://agentskills.io/specification). Copiez l'intégralité de `.agents/skills/orka/` dans le répertoire documenté par votre application, ou indiquez une destination exacte :

```sh
python3 install.py --destination /chemin/des/skills/orka
```

Un modèle seul ne suffit pas : l'application qui l'utilise doit prendre en charge les skills ou pouvoir lire ces fichiers et leurs références. Sans prise en charge native, vous pouvez fournir les fichiers manuellement ; leur découverte automatique n'est pas disponible. La compatibilité avec toutes les applications IA n'est pas garantie.

## Première mission

Après avoir invoqué Orka dans votre assistant :

> Étudie un outil de prise de rendez-vous pour les coachs sportifs indépendants en France. Examine les concurrents, les besoins et les hypothèses de prix. Utilise des sous-agents spécialisés si les outils et les autorisations le permettent, organise les objections et produis un dossier de décision avec sources, incertitudes et prochain test de validation.

Vous pouvez aussi demander directement un plan marketing, la réalisation d'une fonctionnalité autorisée ou une synthèse des retours clients. Précisez le résultat attendu, le projet, les fichiers utiles et les contraintes connues.

Le coordinateur cadre la mission, attribue les tâches, organise les travaux prêts puis vérifie les résultats sur leurs critères. Si les sous-agents ne sont pas disponibles, il applique successivement les points de vue et le signale. Une mission ciblée mobilise seulement les rôles utiles ; les 28 postes n'impliquent pas 28 agents simultanés.

Contacter des tiers, dépenser, publier ou déployer nécessite une autorisation couvrant l'action.

## Compatibilité et limites actuelles

- Les instructions, rôles, workflows et modèles de documents sont partageables entre applications. Les références détaillées sont en français ; les livrables suivent la langue demandée.
- Les modèles disponibles, leurs réglages, la recherche, la délégation et l'accès aux fichiers dépendent de chaque assistant. Le catalogue fourni et le préparateur JSON ciblent les paramètres Codex : ils ne configurent pas Claude.
- Le préparateur de mandats et le registre SQLite sont facultatifs. Le registre appelle le préparateur et partage ses contraintes de catalogue. Sur un autre hôte sans catalogue compatible, utilisez les mandats et le suivi documentaire avec les réglages natifs.
- Aucun de ces outils ne lance de modèle, n'arrête d'agent ou ne fonctionne en permanence. Les tests locaux vérifient les outils, l'installation et l'archive ; chaque plateforme n'a pas fait l'objet d'une évaluation complète avec des modèles réels.

## Documentation et développement

Le [README anglais](README.md#documentation) présente l'index complet. Points d'entrée : [rôles](.agents/skills/orka/references/roles.md), [workflows](.agents/skills/orka/references/workflows-entreprise.md), [orchestration](.agents/skills/orka/references/orchestration-agents.md), [supervision locale](.agents/skills/orka/references/supervision-locale.md), [modèles](.agents/skills/orka/references/modeles-effort.md) et [implémentation](docs/IMPLEMENTATION.md).

Les dossiers de mission produit utilisent `projets/<id>/` ; les missions transversales utilisent `entreprise/missions/<id>/`. Le code applicatif reste dans son dépôt de développement. Conservez les données privées de mission hors de ce dépôt de distribution public. Les exemples du registre utilisent le dossier local ignoré `.orka/`.

```sh
python3 -B .agents/skills/orka/scripts/test_preparer_agent.py
python3 -B .agents/skills/orka/scripts/test_superviser.py
python3 -B -m unittest discover -s tests
python3 install.py --archive dist/orka.zip
```

Pour mettre à jour : examinez les changements, sauvegardez vos adaptations, supprimez l'ancien dossier installé `orka`, puis relancez l'installation. Pour désinstaller, supprimez uniquement ce dossier ; les livrables de mission restent en place. Les contributions peuvent passer par les issues et pull requests, avec le problème observé et les vérifications pertinentes.

Licence [MIT](LICENSE), incluse dans les installations et l'archive. Références de format et d'installation : [OpenAI](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills). L'organisation et les workflows d'Orka sont les choix de ce projet.
