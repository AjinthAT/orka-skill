# Implémentation d’Orka

Propriétaire : coordinateur de maintenance. Version documentaire : 5, 27 octobre 2026. Périmètre : aperçu de la candidate 0.9.0 et des composants existants. Les procédures détaillées restent dans les références liées ; l'historique des changements reste dans Git et les rapports de validation.

## Ce qui fonctionne aujourd’hui

**Le cœur est un dossier Markdown utilisable sans Python.** Le [skill](../.agents/skills/orka/SKILL.md) guide un assistant hôte pour cadrer une mission, choisir parmi 28 rôles et 8 équipes, organiser les travaux et vérifier les résultats. L’assistant fournit ses modèles, outils, accès et éventuels sous-agents. Sans délégation autorisée et disponible, les points de vue sont traités successivement et ce mode est déclaré.

Le coordinateur est l’agent principal de la session. Les rôles sont des responsabilités, pas 28 processus à lancer. L’[orchestration](../.agents/skills/orka/references/orchestration-agents.md) décrit mandats, capacité commune, propriétaires des fichiers, dépendances, échanges et reprise. Les limites de l’hôte et de la mission s’appliquent à toutes les délégations.

Les missions produit sont suivies sous `projets/<id>/`, les missions transversales sous `entreprise/missions/<id>/`. Le code reste dans son dépôt désigné. Les fichiers conservent l’état et les preuves ; ils ne relancent rien seuls et ne constituent pas une sauvegarde automatique.

## Procédures documentaires

La candidate 0.9.0 ajoute le [mode autonome portable](../.agents/skills/orka/references/autonomie.md) : décisions déléguées, fonction de juge attribuée aux rôles existants, poursuite après remise et point de reprise. Son [premier lot AUT-01](LOT-AUT-01.md) définit périmètre et critères. Il s'agit de consignes exécutées avec les outils natifs de l'hôte, pas d'un nouveau service. La reprise reste déclenchée par l'hôte ou une instruction ; aucune continuation après fermeture n'est fournie par ces fichiers.

La [réception ciblée](../evals/autonomie-AUT-01-2026-10-27/README.md) compare trois cas locaux par version, puis vérifie suspension et reprise sans Python. Les contrôles sur pièces sont satisfaits dans les deux versions ; aucun gain général ou comparatif n'est démontré. Le suivi documentaire est possible aussi sous Codex ; l'utilisation d'un registre existant ne peut pas être contournée par un changement silencieux de mode.

| Besoin | Référence |
|---|---|
| Étude, marketing, vente, développement, lancement, support, finance, RH ou pilotage | [Workflows](../.agents/skills/orka/references/workflows-entreprise.md) et [équipes](../.agents/skills/orka/references/roles.md) |
| Adapter l’effort, répartir les tâches et accepter un résultat | [Pilotage des missions](../.agents/skills/orka/references/pilotage-missions.md) |
| Compléter une entrée décisive sans tout recopier | [Contexte progressif](../.agents/skills/orka/references/prompting-agents.md#compléter-le-contexte-par-passes-bornées) et [suivi compact](../.agents/skills/orka/references/modeles.md#suivi-des-compléments-de-contexte) |
| Réviser une décision, transmettre, traiter un incident ou clore | [Processus communs](../.agents/skills/orka/references/processus-transverses.md) et [gestion documentaire](../.agents/skills/orka/references/gestion-documentaire.md) |
| Cadrer vision, preuves, innovation et expériences | [Vision](../.agents/skills/orka/references/vision-preuves-innovation.md) et [expériences](../.agents/skills/orka/references/experiences-apprentissage.md) |
| Allouer les ressources IA ou proposer un nom | [Ressources IA](../.agents/skills/orka/references/ressources-agents.md) et [noms/domaines](../.agents/skills/orka/references/noms-domaines.md) |

L2 conserve un plafond de compléments commun à la tâche, trois par défaut, à travers les tentatives. Les réponses gardent provenance, version et effet sur les conclusions ; une nouvelle version décisive fait réexaminer les dépendants sans effacer l’ancienne preuve. Fourni, lecture déclarée et lecture observée restent distincts. Ce suivi fonctionne par édition de texte et échanges natifs ; il n’ajoute aucun compteur technique de lectures, de droits ou de tokens.

Les guides de démarrage [français](../.agents/skills/orka/GUIDE.fr.md) et [anglais](../.agents/skills/orka/GUIDE.md) sont inclus dans le paquet. Le prochain prompt proposé en fin de réponse reste une suggestion ; il ne lance pas automatiquement une phase supplémentaire.

## Outils locaux facultatifs

Ces outils nécessitent Python 3.10+ et sa bibliothèque standard, sans SDK ni paquet tiers. Ils ne lancent aucun modèle, ne collectent pas les sessions et ne changent pas les paramètres personnels. L’installation par copie ou import ZIP et l’usage documentaire restent sans Python.

| Outil | Fonction disponible | Limite principale |
|---|---|---|
| [Installateur](../install.py) | Copier le skill complet ou construire son ZIP, licence comprise | Refuse une destination existante ; aucun téléchargement ni activation de l’hôte |
| [Préparateur Codex](../.agents/skills/orka/scripts/preparer_agent.py) | Valider le mandat et composer consignes communes, fiche du rôle et requête | Catalogue Codex fourni ; paramètres appliqués inconnus et état préparé non lancé |
| [Préparateur Claude](../.agents/skills/orka/scripts/preparer_agent_claude.py) | Valider le même mandat et exporter une définition native Claude Code/Agent SDK | Catalogue documentaire distinct ; ne configure pas les permissions et ne raccorde pas le registre |
| [Registre Codex](../.agents/skills/orka/scripts/superviser.py) | Persister tâches, réservations, tentatives, versions et événements dans SQLite | Identités et fins de rédacteurs déclarées par le coordinateur ; ne contrôle pas les processus extérieurs |
| [Bilan](../.agents/skills/orka/scripts/bilan_agents.py) | Agréger un relevé fourni avec couverture, dénominateurs et coûts séparés | Pas de collecte, tarification automatique ou détection d’omissions dissimulées |
| [Diagnostic](../.agents/skills/orka/scripts/diagnostiquer.py) | Examiner un dossier explicite en lecture seule et comparer une référence facultative | Pas de réparation, d’authentification de la référence ou de preuve d’activation |

### Mandats et réglages

Le [contrat de mandat](../.agents/skills/orka/references/prompting-agents.md) conserve modes, tentatives, critères et réglages explicites. Les clés inconnues ou dupliquées et les couples modèle/effort incompatibles sont refusés. Le préparateur produit des empreintes de prompt et de requête, sans prouver leur lecture ou leur exécution. Les [profils RH Claude](../.agents/skills/orka/references/modeles-effort-claude.md) conservent les mêmes rôles et règles métier avec un catalogue et un export natifs distincts. La disponibilité du compte reste à vérifier ; aucun repli automatique. Sur un hôte sans catalogue compatible, utiliser les documents et réglages natifs.

### Supervision et conservation

Le [guide de supervision](../.agents/skills/orka/references/supervision-locale.md) est la référence pour le schéma SQLite v2, les commandes et les migrations. Les contrôles suivent les dépendances indirectes et les versions d’entrées déclarées. Une source réacceptée, même identique, ne valide pas silencieusement les anciennes sorties dépendantes.

Réservation, rattachement à une exécution, remise, confirmation de fin et acceptation restent distincts. Une réservation inactive n’est pas libérée automatiquement. Le réexamen exige motif, responsable et absence de rédacteur actif ; les anciennes preuves sont conservées. Une base v1 nécessite une migration explicite avec sauvegarde cohérente, journal WAL compris ; ses anciennes versions d’entrées restent inconnues.

Le registre ne verrouille pas les écritures qui le contournent. Plafond financier, annulation de tâche, modification d’un mandat enregistré et arrêt des agents extérieurs ne sont pas implémentés par cette interface.

### Mesures et diagnostic

Le [bilan](../.agents/skills/orka/references/bilan-agents.md) garde les valeurs absentes inconnues et sépare devises, nature des montants et sous-totaux. La longueur des textes ne devient pas une mesure de consommation.

Le [diagnostic](../.agents/skills/orka/references/diagnostic-installation.md) documente les formats reconnus, exclusions, liens non suivis et contrôles manuels. Un dossier conforme ne prouve ni son chargement ni les capacités de l’hôte ; une comparaison d’empreintes ne certifie pas la sécurité du code ou la provenance de la référence.

## Vérification et évaluations

Le [guide de contribution](../CONTRIBUTING.md) centralise les commandes de vérification et de construction. Le [vérificateur](../tools/verifier.py) contrôle métadonnées, liens maintenus, suites après installation déplacée et contenu du ZIP. PyYAML reste une dépendance de maintenance seulement. Les sorties des outils sont en UTF-8 et les régressions incluent des sous-processus sous configuration ASCII.

L’outil de maintenance [evaluer.py](../tools/evaluer.py), hors ZIP installé, fige les campagnes et importe des observations sans lancer de modèle. Le [guide de formats](EVALUATIONS.md) distingue contrôles JSON et revues attribuées ; la [réception L3](VALIDATION-L3.md) utilise uniquement des données simulées.

La [matrice CI](../.github/workflows/verification.yml) couvre Linux/macOS/Windows avec Python 3.10 et 3.13. Le tag doit correspondre à la version déclarée. Une configuration de CI ne prouve pas qu’une exécution donnée a réussi : consulter ses résultats.

Les [évaluations conservées](../evals/README.md) distinguent pilote comparatif 0.4.0, découverte depuis le README et réception ciblée L2. Les [preuves L1](VALIDATION-L1.md) et [L2](VALIDATION-L2.md) décrivent leur portée. Ni les tests logiciels ni les essais ciblés n’établissent un gain général de qualité ou de coût ; les réglages appliqués et mesures absents restent inconnus. Les originaux sont conservés hors du paquet installé.

La [réception RH Claude](VALIDATION-RH-CLAUDE.md) documente le catalogue et l'export natif 0.8.0, les régressions hors ligne et les fichiers figés préservés. Elle ne qualifie pas les performances des modèles ni leur disponibilité sur un compte.

## Ce qui reste à construire

Le [lot ECC-01](LOT-ECC-01.md) distingue L1 livré en 0.5.0, L2 en 0.6.0 et L3, outillage d’évaluations répétées livré en 0.7.0 sur données simulées. La [préparation L4](../evals/preparation-L4-2026-10-22/README.md) fige trois nouveaux cas, deux versions et 18 lignes non lancées ; le réservé et les grilles exactes restent locaux. L4, qualification comparative, reste à réaliser. La procédure d’[évaluation des agents](../.agents/skills/orka/references/evaluation-agents.md) porte les autres renforcements à éprouver.

Une application autonome demanderait encore un client de lancement relié au registre, un ordonnanceur, une messagerie persistante, des contrôles effectifs d’accès et de moyens, la réconciliation après interruption et éventuellement une interface de suivi. Le stockage et la restauration nécessiteraient leur propre dispositif vérifié. Aucun service permanent, collecte automatique, programmation continue ou arrêt financier n’est fourni par les fichiers du skill.

Ces extensions restent des propositions. Leur périmètre dépend d’un besoin et d’une mission autorisés ; elles ne tournent pas en arrière-plan après installation.
