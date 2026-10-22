# Validation L2 — contexte progressif 0.6.0

Propriétaire : coordinateur de maintenance. Version : 1. Date : 22 octobre 2026. Périmètre : [ECC-01 L2](LOT-ECC-01.md), réception C1–C5 et conservation des interfaces existantes. Réalisation originale Orka, sans reprise de code ou texte ECC.

## Livré

- [Protocole canonique](../.agents/skills/orka/references/prompting-agents.md#compléter-le-contexte-par-passes-bornées) : entrées initiales ciblées, compléments motivés, trois demandes par tâche par défaut, relances comptées, cumul conservé à la reprise et point d'arrêt explicite.
- [Suivi compact avec exemple fictif](../.agents/skills/orka/references/modeles.md#suivi-des-compléments-de-contexte) : provenance, version connue ou inconnue, réponse/indisponibilité, états de lecture, effet sur la conclusion et réexamen des dépendances.
- Intégration à l'[orchestration](../.agents/skills/orka/references/orchestration-agents.md#gestion-de-la-mémoire), aux [consignes préparées des spécialistes](../.agents/skills/orka/references/prompts/consignes-communes.md), au skill et aux guides bilingues. Aucun chargement systématique de tout l'historique.

## Preuves de réception

Les [trois cas fictifs et leurs sorties](../evals/contexte-L2-2026-10-22/README.md), les [critères prédéfinis](../evals/contexte-L2-2026-10-22/criteres.json) et la [revue par critère](../evals/contexte-L2-2026-10-22/revue.md) couvrent : C1 tâche complète ; C2 devis demandé et conclusion corrigée ; C3 reprise au plafond avec coût inaccessible ; C4 changement décisif et historique conservé ; C5 contenu hostile non adopté dans la sortie. C5 reste limité aux preuves disponibles, sans audit indépendant des accès. Un essai par cas ne prouve pas une application systématique.

Le parcours utilise les documents et outils de fichiers de l'hôte, sans exécuter Python pour traiter les missions. La préparation des données, les empreintes et les tests logiciels utilisent Python séparément. La machine possède Python ; elle n'est pas présentée comme un hôte qui en est dépourvu. Le modèle de suivi reste exploitable par simple édition de texte.

Le [contrôle de compatibilité du préparateur](../evals/contexte-L2-2026-10-22/compatibilite-preparateur.json) vérifie un mandat de reprise : contexte, entrées et limites conservés dans les champs existants, modèle/effort explicites et tentative conservés, état préparé non lancé, paramètres appliqués inconnus. Il ne lance aucun modèle. Aucun nouveau champ JSON, catalogue, script ou schéma SQLite n'est ajouté. Les scripts existants restent inchangés ; leurs suites et les contrôles de distribution restent exécutés par [le vérificateur](../tools/verifier.py), notamment dans une installation déplacée.

Les nouveaux documents du paquet sont comparés à la distribution construite ; le diagnostic L1 peut comparer une copie installée temporaire à l'archive extraite. Le [workflow de vérification](../.github/workflows/verification.yml) couvre Linux/macOS/Windows avec Python 3.10/3.13 ; sa présence n'est pas un résultat distant. Consulter les [exécutions du commit/tag publié](https://github.com/AjinthAT/orka-skill/actions/workflows/verification.yml) pour les résultats observés.

## Conservation et limites

Les anciens répertoires d'évaluation et leurs empreintes sont conservés ; les nouvelles preuves vont dans un dossier distinct. Aucun registre de mission n'est lu ou migré, aucune installation personnelle ni configuration de l'hôte n'est mise à jour. Les paramètres modèle/effort des profils restent inchangés ; une demande de contexte ne vaut pas un changement de modèle.

Le plafond et les états de lecture sont des conventions documentaires, pas des contrôles techniques d'accès ou de tokens. Les réglages appliqués et consommations absents restent inconnus. La copie gelée, les consignes de lecture et les traces disponibles ne remplacent pas une sandbox ni un audit indépendant. Aucun gain économique ou de qualité n'est établi. C6 et la qualification comparative répétée L4 restent non exécutés ; L3 n'est pas implémentée par cette livraison.
