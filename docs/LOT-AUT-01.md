# AUT 01 Mode autonome portable

Propriétaire : coordinateur de maintenance. Version : 1. Date : 27 octobre 2026. Référence : commit `0d4f197`, distribution 0.8.0. Candidate : 0.9.0 locale, non publiée.

## Résultat du premier lot

Ajouter au skill un mode autonome explicitement demandé : décisions déléguées, débat ciblé et juge, poursuite du travail déjà autorisé et reprise depuis un état conservé. L'assistant hôte fournit les outils et l'exécution ; le cœur reste utilisable sans Python. La demande utilisateur porte sur l'évolution d'Orka dans ce dépôt, en réutilisant ses composants.

La référence métier unique sera [autonomie.md](../.agents/skills/orka/references/autonomie.md). Les consignes d'entrée, modèles de suivi et guides pointeront vers elle. Le juge est une fonction attribuée aux rôles existants, pas un nouveau rôle ajouté au catalogue. Le registre SQLite existant reste facultatif, sans migration de schéma. Ses garanties ne sont pas étendues par du texte.

## Périmètre et fichiers

| Pièce | Changement |
|---|---|
| `SKILL.md` | Activation, routage et poursuite avant restitution finale |
| `references/autonomie.md` | Mandat, arbitrage, boucle de travail et reprise ; limite entre skill et lanceur |
| `references/modeles.md` | Champs compacts d'autonomie, décisions déléguées et point de reprise |
| `references/collaboration.md`, `roles.md`, `orchestration-agents.md` | Rattachement de l'arbitrage à une délégation réelle, sans double autorité |
| Guides FR/EN et README FR/EN | Invocation et capacités réellement disponibles |
| `references/validation.md`, dossier d'évaluation AUT-01 | Scénarios et preuves de la vérification ciblée |
| `docs/IMPLEMENTATION.md` | État livré, limites et suite facultative |

Ce lot ne raccorde ni SDK réel ni nouveau fournisseur. Il ne modifie pas les prototypes hors ligne, leurs contrats, les campagnes L4 ou les captures historiques. Il n'installe pas de daemon, programmation, télémétrie, limite financière technique ou mécanisme d'arrêt de processus. L'export ZIP sera vérifié ; l'installation personnelle ne sera pas remplacée implicitement.

## Critères de validation

| ID | Observation requise |
|---|---|
| C1 | Une demande explicite d'autonomie active le mode sans imposer une seconde confirmation ; une simple question ou un plan n'autorise pas la réalisation. |
| C2 | Objectif, périmètre, choix délégués, exceptions et limites sont déduits des instructions existantes et conservés ; moyens inconnus signalés sans budget inventé. |
| C3 | Un désaccord matériel est tranché sur contraintes et preuves, ou conduit à un test autorisé ; un vote n'est pas une preuve. Les auteurs et l'arbitre sont identifiés. |
| C4 | Une décision dans la délégation est exécutée et les tâches prêtes suivantes poursuivies sans demander « continue » ; aucune phase nouvelle non autorisée. |
| C5 | Sans sous-agents, perspectives successives et autocontrôle sont déclarés ; aucun spécialiste fictif. |
| C6 | Le point de reprise conserve tâches, versions, décisions, compteurs et prochaines actions ; après reprise, les sorties périmées sont réexaminées. |
| C7 | Un effet inconnu ou un rédacteur dont l'arrêt est inconnu ne déclenche pas de relance aveugle ; les travaux indépendants continuent. |
| C8 | Limite atteinte, suspension explicite ou mandat insuffisant produisent une sortie partielle fidèle ; ni faux achèvement ni promesse de redémarrage automatique. |
| C9 | Les références sont embarquées dans le ZIP et restent accessibles après déplacement ; l'usage documentaire ne nécessite aucun nouveau paquet ou script. |
| C10 | Référence et candidate sont comparées sur les mêmes entrées ; résultats et limites conservés. Aucun gain général de qualité, coût ou autonomie permanente n'est déduit de ce pilote. |

## Vérification prévue avant remise

Contrôles de format du skill, liens, distribution et suites existantes via le vérificateur du dépôt. Puis comparaison bornée 0.8.0/candidate sur trois cas synthétiques en deux contextes séparés, avec un seul passage par condition ; les trois cas d'une condition partagent leur contexte. Les critères restent hors du contexte de production. Un cas distinct, réservé avant modification et exécuté après gel de la candidate, fournit une vérification finale ciblée. Le modèle et l'effort restent ceux hérités de l'hôte ; consommation et paramètres non observés restent inconnus.

Les exécutions ne peuvent écrire que dans leurs espaces temporaires, sans Web, contact, dépense ou descendant. Le coordinateur vérifie les artefacts, les compteurs et les actions effectives ; des instructions hostiles font partie des données fictives. Un résultat inconclusif ou un échec est conservé. Ces essais évaluent un comportement local, sans qualification multi-hôtes, reprise après crash réel ou test financier.

## Réception du lot portable

Le [rapport ciblé](../evals/autonomie-AUT-01-2026-10-27/README.md) conserve critères, versions, entrées, réponses et limites. Les trois cas comparatifs satisfont les contrôles sur pièces dans chaque condition, sans avantage établi sur 0.8.0. C04 vérifie la suspension sur r1 ; après correction de l'optionalité du registre, le nouveau C05 vérifie la reprise documentaire sans Python sur r2. Le juge multiagent distinct, le crash réel et le contrôle financier restent hors de cette qualification. Les vérifications logicielles et du paquet sont consignées après leur exécution.

Contrôles exécutés sur cet hôte Linux : `quick_validate.py` valide le skill ; `tools/verifier.py` termine avec 131 tests listés, dont 41 opt-in ignorés, puis vérifie les octets du paquet portable. Le [journal de vérification](../evals/autonomie-AUT-01-2026-10-27/verification-depot.txt) conserve le résultat. Les suites SDK/Docker opt-in ne sont pas déclarées exécutées ; aucune matrice multi-plateforme n'a été rejouée.

## Suite facultative

Après ce lot, un lanceur dans le même dépôt pourrait relier exécutions réelles, registre, reprise et contrôles techniques. Son contrat devra identifier l'autorité d'état, les droits, la réconciliation des effets et les limites mesurables. Cette suite reste distincte du mode portable et des prototypes actuels ; aucun lancement permanent n'est annoncé par AUT-01.
