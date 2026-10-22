# Réception L3 — préparation et bilan d’évaluations répétées

Propriétaire : coordinateur de maintenance. Version : 1. Date : 22 octobre 2026. Référence précédente : `0de7b39`, Orka 0.6.0. Candidate : 0.7.0. Périmètre : [ECC-01 L3](LOT-ECC-01.md), logiciel et procédure documentaire. **Aucun modèle ni agent d’évaluation lancé.** Conception originale Orka, sans reprise de code ou texte ECC.

## Existant et ajouts

Le préparateur de mandats, le registre SQLite, le bilan de relevés fournis et les captures d’évaluation existaient déjà. L3 ajoute [tools/evaluer.py](../tools/evaluer.py), ses [formats et commandes](EVALUATIONS.md), les [régressions](../tests/test_evaluer.py) et un [exemple de bilan sur observations fabriquées](../evals/outillage-L3-2026-10-22/README.md). L’outil reste propre au dépôt, hors ZIP installé, Python 3.10+ et bibliothèque standard seulement. Les tests sont découverts par le vérificateur existant.

La [procédure manuelle](../.agents/skills/orka/references/evaluation-agents.md#préparer-et-relire-des-répétitions) complète les instructions du skill. Elle fixe une matrice et conserve sources, critères, résultats, états et dénominateurs dans des documents ordinaires ; Python n’est pas nécessaire pour ce parcours.

## Critères vérifiés

| Critère | Preuve logicielle et observation |
|---|---|
| E1 — préparation figée | `test_preparation_freezes_complete_matrix_without_execution` : cas, critères, instructions, prompts exacts, répétitions, ordre et limites conservés ; six slots préparés et zéro exécution réelle déclarée. L’import refuse l’état préparé comme résultat exécuté. Le [manifeste de simulation](../evals/outillage-L3-2026-10-22/demonstration-simulee/manifest.json) distingue explicitement observations fabriquées et réelles. |
| E2 — refus et reprise partielle | Tests d’identifiants dupliqués, clés dupliquées, champs inconnus, maximum dépassé, destinations existantes, résultats sans provenance ou empreinte cohérente, sortie figée modifiée et import répété. Les déclarations originales sont conservées octet pour octet. Les essais de corruption bloquent le bilan ; les interruptions donnent un rapport partiel sans inventer les lignes manquantes. Une reprise utilise un nouveau plan lié à l’original, sans remplacement. |
| E3 — critères de fond | `test_checks_evaluate_structured_values_not_presence_of_a_phrase`, sorties absentes/mal formées/de mauvais type et revue manquante : 121 ne satisfait pas un total attendu de 120, et un booléen ne vaut pas un nombre. Les bornes vérifient la marge 30. Les critères métier restent `revue_attribuee`, sans verdict automatique si aucune revue n’est fournie. Les contrôles exécutables sont refusés. |
| E4 — toutes les répétitions | `test_mixed_repetitions_keep_every_outcome_and_denominator` et [bilan conservé](../evals/outillage-L3-2026-10-22/bilan.json) : six slots, cinq observations simulées, un succès, un échec, une interruption, un hors protocole, un inconclusif et un préparé. Taux comparable 1/2, succès sur prévus 1/6, détails et compteurs par critère/condition conservés. Aucun meilleur résultat n’est sélectionné. |
| E5 — inconnues et mesures | Tests de mesures partielles, devises/natures séparées, identifiants de mesure réutilisés, cumuls refusés, réglages appliqués inconnus ou différents et durée murale. Les tokens inconnus restent null ; les sous-totaux fournis gardent leur couverture. Les montants de l’exemple sont fabriqués, sans tarif réel ni gain annoncé. Aucun paramètre appliqué n’est inféré de la demande ou de la longueur des textes. |
| E6 — conservation et rejeu | `test_prototypes_and_existing_register_are_never_executed_or_modified` : sortie Python copiée et hachée sans exécution, fichiers source et base SQLite de fixture inchangés. Tests de bilan en lecture seule et de copie déplacée. Les jeux publics antérieurs sont comparés par SHA-256 avant/après maintenance, sans réécriture de leurs sorties, index internes, manifests ou empreintes. Le nouvel index parent ne modifie pas ces preuves. Le test de checkout CRLF vérifie la protection des octets fournie par `.gitattributes`, sans renormaliser les captures. |

Les 25 tests de l’outil sont des tests de logiciel sur données fabriquées. Ils ne sont pas des réponses de modèles reproduites. La [matrice CI](../.github/workflows/verification.yml) exécute le même vérificateur sur Linux/macOS/Windows avec Python 3.10 et 3.13 ; consulter les [résultats du commit/tag publié](https://github.com/AjinthAT/orka-skill/actions/workflows/verification.yml), sans déduire leur réussite de la seule configuration.

## Parcours sans Python

Un [comptage manuel conservé](../evals/outillage-L3-2026-10-22/controle-manuel.md) reprend la matrice fictive ci-dessus : inscrire six lignes, leur état et leur preuve ; compter séparément les deux lignes évaluables, les quatre autres issues et les mesures absentes. Cette lecture et l’édition d’un tableau ne nécessitent aucune exécution Python. Les tests automatisés, le gel des fichiers et le calcul des empreintes utilisent Python séparément. La machine de maintenance dispose de Python ; ce n’est pas un essai d’hôte physiquement dépourvu de Python, et aucun nouvel essai comportemental d’agent n’a été lancé pour ce contrôle documentaire.

## Conservation et limites

Le catalogue modèle/effort, les helpers installés, le schéma SQLite v2 et les données de mission restent inchangés. Les installations personnelles ne sont pas mises à jour. Les nouvelles preuves sont dans un dossier séparé, distinct des campagnes réelles antérieures. L’origine simulée des instructions, sorties, revues et mesures reste visible dans les données et leur index.

Un rejeu CLI complet dans une copie temporaire (préparation, cinq imports et bilan) reproduit exactement le rapport logiciel conservé. Ce rejeu utilise Python sans paquet tiers, ne lance aucun modèle et ne remplace aucune observation originale.

Les états, identités et preuves importés sont des déclarations de l’opérateur. Empreintes et contrôles statiques ne certifient ni leur authenticité, ni une sandbox, ni l’absence de lecture hors périmètre. Les limites d’accès, de coût et d’agents doivent être appliquées par l’hôte et le coordinateur. Les compteurs de slots ne comptent pas implicitement les spécialistes et le coordinateur de campagne.

L’outil ne fusionne pas les campagnes de reprise et ne recueille aucune télémétrie. La décision L4/E7 reste séparée : les échecs, inconnues et écarts doivent être examinés, sans promotion automatique d’une candidate. Aucune campagne L4, qualification C6, comparaison économique ou amélioration générale n’est établie par cette réception logicielle.
