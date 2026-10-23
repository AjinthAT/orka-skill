# Réception logicielle des profils RH Claude

Propriétaire : coordinateur de maintenance. Version : 1, 23 octobre 2026. État : contrôles locaux réussis ; aucune qualification comparative de modèles. Périmètre : ajout distribué en 0.8.0, sans publication ni mise à jour des installations personnelles.

## Changement et critères

La demande est d'ajouter les modèles Claude aux ressources RH comme pour Codex. Le [catalogue distinct](../.agents/skills/orka/references/profils-modeles-claude.json) conserve six profils, 28 rôles et huit équipes. Le [guide Claude](../.agents/skills/orka/references/modeles-effort-claude.md) donne les sources datées, allocations proposées et limites. Le [préparateur natif](../.agents/skills/orka/scripts/preparer_agent_claude.py) partage les validations du mandat existant ; il exporte des définitions Claude Code/Agent SDK sans convertir les chaînes d'outils du mandat en permissions.

Critères vérifiés :

- Chaque rôle reçoit son modèle et effort Claude, avec le même mandat et ses critères.
- Les surcharges explicites sont conservées ; les modèles, efforts et capacités incompatibles sont refusés sans substitution.
- L'export ne contient pas les clés de lancement Codex ; son état est préparé, ses paramètres appliqués inconnus et ses empreintes distinguent les tentatives et efforts.
- La CLI reste UTF-8 sous configuration ASCII et refuse écrasement, collision avec le livrable et clés JSON dupliquées.
- Le préparateur public Codex garde son format et ses réglages par défaut ; le catalogue Codex et le superviseur sont conservés.

## Résultats observés

Le 23 octobre 2026 sur macOS, Python 3.12 :

- **11 tests Claude** et **13 tests du préparateur Codex** réussis. Les nouveaux tests rejoignent aussi les suites exécutées après installation dans un dossier temporaire.
- Construction hors ligne de **28 `AgentDefinition`** avec `claude-agent-sdk==0.2.173`, sans créer de client ni exécuter Claude Code. Tous les modèles et efforts demandés sont conservés par les objets.
- `python -B tools/verifier.py` : **131 tests recensés, 68 exécutés avec succès et 63 ignorés** selon leurs conditions de plateforme ou d'activation explicite ; métadonnées 0.8.0, liens locaux et ZIP portable vérifiés. Les suites de scripts installés sont exécutées à l'intérieur des tests de distribution.
- Comparaison SHA-256 avant/après de **247 fichiers protégés** : aucun changement. Le périmètre comprend les captures suivies sous `evals/`, tous les fichiers sources et contrats du prototype SDK–Inspect, le catalogue Codex et les scripts de supervision déjà corrigés.
- `git diff --check` réussi.

Aucun appel modèle, lancement d'agent, accès aux comptes Claude ou modification des paramètres personnels. Les suites optionnelles Docker/SDK/Inspect existantes n'ont pas été relancées : leurs sources et contrats sont inchangés. L4 est préservé. Le succès logiciel ne prouve ni disponibilité des modèles sur le compte, ni respect effectif de l'allocation par l'hôte, ni gain de qualité ou de coût.
