# Profils RH pour Claude

Propriétaire : DRH IA et coordinateur de maintenance. Version : 1, 23 octobre 2026. État : référence pour la préparation hors ligne ; allocation proposée, sans qualification comparative des modèles. Provenance : documentation Anthropic liée ci-dessous. La disponibilité sur le compte de l'utilisateur reste inconnue.

## Allocation proposée

Le [catalogue Claude](profils-modeles-claude.json) reprend les six profils, 28 rôles et huit équipes du [catalogue Codex](profils-modeles.json), avec des paramètres natifs distincts. Les mêmes règles de [choix et d'escalade](modeles-effort.md) et de [gestion des ressources](ressources-agents.md) s'appliquent. Le titre du poste ne détermine pas un modèle permanent.

| Profil | Modèle demandé | Effort | Usage proposé |
|---|---|---|---|
| coordination | claude-opus-5-5 | high | Décomposition, dépendances et synthèse |
| execution | claude-haiku-5-5 | medium | Traitement borné de faits établis |
| analyse | claude-sonnet-5-5 | medium | Recherche, comparaison et synthèse |
| realisation | claude-sonnet-5-5 | high | Conception, développement et exploitation |
| revue | claude-opus-5-5 | high | Contrôle critique et qualité |
| expertise | claude-fable-5-1 | high | Difficulté persistante après correction du contexte et essai avec Opus |

Ces allocations sont la politique proposée d'Orka, pas un classement mesuré. Le profil expertise est conditionné à une difficulté identifiée et à la disponibilité réelle de Fable. S'il est indisponible, le préparateur refuse la demande ; aucun remplacement automatique. Un choix explicite d'Opus avec un effort supérieur compatible reste possible dans les limites du mandat. Aucune consommation, économie ou tarification n'est déduite du nom d'un modèle.

Les quatre identifiants ci-dessus sont documentés avec `low`, `medium`, `high`, `xhigh` et `max` à la date de consultation. Le catalogue refuse les alias courts variables (`sonnet`, `opus`, etc.), les modèles étrangers et les efforts absents. `ultra` n'est pas un effort Claude ; `ultracode` désigne un mode de travail Claude Code, pas une valeur d'effort. Ne pas choisir automatiquement `max`.

## Préparation native, sans lancement

Le [préparateur Claude](../scripts/preparer_agent_claude.py) partage la validation du mandat, les consignes communes et la fiche de rôle avec le préparateur Codex. Il utilise uniquement Python 3.10+ et la bibliothèque standard. Depuis la racine du dépôt :

```sh
python3 -B .agents/skills/orka/scripts/preparer_agent_claude.py --mandat .agents/skills/orka/assets/mandat-exemple.json
```

Utiliser `--output` pour créer un nouveau fichier, jamais pour remplacer un livrable ou une requête existante. Les clés inconnues ou dupliquées et les couples incompatibles sont refusés. Le [contrat du mandat](prompting-agents.md) reste identique, avec `profil`, `modele` et `effort` facultatifs.

`--capacites` accepte le même format de capacités déclarées : identifiant complet du modèle associé à une liste d'efforts. Exemple de forme uniquement, à remplacer par le relevé réel du coordinateur :

```json
{"claude-haiku-5-5": ["medium"]}
```

Sans ce fichier, `verification_capacites` reste `a_verifier_au_lancement`. Une déclaration ne prouve ni accès au compte, ni modèle réellement utilisé. L'état reste `prepare_non_lance` et `parametres_appliques` reste nul.

L'enveloppe de sortie porte `format: orka-claude-agent-definitions`, `version: 1`, `hote: claude`, le profil, la tentative et les empreintes. `parametres_demandes.agents` contient une définition nommée avec `description`, `prompt`, `model` et `effort`. Cette table correspond aux définitions `--agents` de Claude Code et à `agents={nom: AgentDefinition(**definition)}` du Claude Agent SDK Python. Le coordinateur doit sélectionner la définition avec les outils disponibles. L'enveloppe complète n'est pas un argument de lancement ; aucun client ni agent n'est créé par ce script. Le nom inclut la tentative et fait partie de l'empreinte de requête.

Ne pas transmettre les clés Codex `fork_turns` ou `reasoning_effort`. L'API Messages directe emploie `output_config.effort` : cet export ne vise pas cette API. Aucun fichier natif d'agent persistant, paramètre personnel ou variable d'environnement n'est modifié.

## Contrôles avant une éventuelle exécution

Le champ `outils_autorises` reste une instruction du mandat : l'export ne traduit pas ses chaînes en permissions techniques. La définition ne fixe pas `tools` ni `permissionMode` ; Claude peut donc hériter des outils de son hôte. Le coordinateur doit configurer et vérifier les outils et autorisations natifs avant tout lancement. Cet outil RH ne fournit pas l'isolation du prototype à trois outils.

Les réglages de session, politiques du compte et variables telles que `CLAUDE_CODE_EFFORT_LEVEL` ou `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` peuvent modifier le choix effectif. Vérifier la version de l'hôte et ses capacités ; relever les paramètres réellement observés, ou conserver leur état inconnu. Ne pas modifier ces réglages personnels pour appliquer une allocation de mission.

Le registre SQLite actuel appelle le préparateur Codex : ne pas lui transmettre une requête native Claude et ne pas présenter ses réservations comme un raccordement Claude. Utiliser le suivi documentaire et le [bilan des mesures fournies](bilan-agents.md). Les prototypes et évaluations conservés gardent leurs contrats et paramètres figés ; ce catalogue ne les migre pas et ne lance pas L4.

## Sources et qualification

Documentation consultée le 23 octobre 2026 : [modèles et identifiants](https://platform.claude.com/docs/en/models/overview), [modèle et effort dans Claude Code](https://code.claude.com/docs/en/model-config), [définitions des sous-agents](https://code.claude.com/docs/en/sub-agents), [effort dans l'API](https://platform.claude.com/docs/en/build-with-claude/effort). Les champs de définition sont aussi vérifiés hors ligne contre le Claude Agent SDK Python installé ; cela ne démontre pas l'accès aux modèles.

Les [tests du préparateur](../scripts/test_preparer_agent_claude.py) couvrent les rôles, efforts, refus, empreintes, CLI et préservation des défauts Codex. Une qualification de qualité ou de coût exige des exécutions séparément autorisées selon [l'évaluation des agents](evaluation-agents.md), avec critères comparables et mesures disponibles. Aucun appel modèle n'a servi à établir cette allocation.
