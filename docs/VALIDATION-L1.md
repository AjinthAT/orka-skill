# Validation L1 — diagnostic d’installation 0.5.0

Propriétaire : coordinateur de maintenance. Version : 1. Date : 22 octobre 2026. Périmètre : diagnostic facultatif et procédure manuelle du [lot ECC-01](LOT-ECC-01.md). Réalisation originale Orka ; aucun code ECC copié. Aucun modèle métier ni campagne répétée lancé.

## Critères et preuves

| Critère | Vérification |
|---|---|
| D1 — installation déplacée | Test `test_complete_relocated_and_reference_are_read_only` ; test d’installation exécutant les suites dans la copie déplacée. Un ZIP construit du dépôt est extrait puis comparé à une installation temporaire produite par l’installateur : code 0, intégrité conforme. |
| D2 — erreurs lisibles | Tests de `SKILL.md` absent, métadonnées non prises en charge ou dupliquées, version invalide, texte UTF-8 invalide ou trop grand, guide manquant, image/lien local cassé et ancre absente. Les erreurs sont des constats et un code 1 ; arguments invalides : code 2. |
| D3 — adaptations préservées | Test de modification d’un guide, ajout de notes et suppression de licence face à une référence. Inventaire et différences attendus, code 1, fichiers identiques avant/après diagnostic. Sans référence ou avec référence invalide, l’intégrité reste non vérifiée. |
| D4 — périmètre et lecture seule | Tests d’échappement `..`, forme encodée, URL `file:`, chemin Windows, lien symbolique de fichier/dossier, erreur d’accès simulée et jonction Windows. Les lectures des liens sortants sont refusées ; les snapshots des fixtures et du dossier personnel simulé restent identiques. |
| D5 — activation distincte | Une installation correcte conserve `activation_hote: non_verifiee` et `capacites_hote: non_verifiees`, même avec comparaison conforme. Aucun hôte n’est lancé. |
| D6 — distribution et plateformes | Le diagnostic fonctionne avec Python `-S` et sorties configurées ASCII, sans paquet tiers ni exécution du code inspecté. Les 15 tests du diagnostic sont inclus dans les suites après déplacement. La [matrice CI](../.github/workflows/verification.yml) exécute le même vérificateur sur Linux/macOS/Windows, Python 3.10/3.13 ; consulter les résultats du commit ou du tag effectivement publié. |

Les tests se trouvent dans [test_diagnostiquer.py](../.agents/skills/orka/scripts/test_diagnostiquer.py) et [test_install.py](../tests/test_install.py). Les autres suites du préparateur, du registre et du bilan restent exécutées. Le test de jonction est spécifique à Windows et est signalé comme ignoré sur les autres systèmes ; les tests de liens symboliques peuvent être ignorés si le système ne permet pas leur création. Une erreur d’accès est injectée de façon reproductible, sans dépendre de privilèges locaux.

## Parcours manuel sans exécution de Python

Une archive construite est extraite avec l’utilitaire système, puis son dossier complet est copié dans un répertoire de démonstration. Présence de `SKILL.md`, des guides, de la licence et de la référence de diagnostic vérifiée ; début des guides et métadonnées lus sans exécuter de Python pendant ce parcours. La construction du ZIP et les tests automatisés utilisent Python séparément. La machine de validation dispose de Python : cet essai ne prétend pas être réalisé sur un système qui en est dépourvu.

L’activation dans une nouvelle session et les capacités de l’hôte restent à vérifier dans cet hôte. La procédure manuelle ne prouve pas une égalité d’empreintes. Les comparaisons automatisées, elles, portent sur des copies temporaires et n’installent rien dans les dossiers personnels.

## Conservation et limites

Le diagnostic ne propose ni réparation automatique ni modification des paramètres. L’installateur continue de refuser une destination existante ; ses tests vérifient la conservation des adaptations et d’un lien symbolique cassé. Les installations personnelles présentes sont suivies par empreintes pendant la maintenance ; elles ne sont pas mises à jour par cette livraison.

Les données d’évaluation publiques, les scripts du registre et ses profils restent inchangés. Le diagnostic ne lit ni ne migre de registre SQLite. Son inspection statique n’est ni une sandbox contre les mutations concurrentes ni une certification de sécurité du code ou de la provenance de la référence.

La liste des plateformes dans une configuration CI ne prouve pas un résultat distant : les [exécutions GitHub Actions](https://github.com/AjinthAT/orka-skill/actions/workflows/verification.yml) donnent l’état observé pour chaque commit/tag. La release doit être associée à une matrice réussie avant publication.
