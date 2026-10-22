# Bilan local des agents

[bilan_agents.py](../scripts/bilan_agents.py) calcule un bilan à partir d'un relevé JSON fourni. Il ne lance aucun agent, ne collecte aucune mesure et ne modifie pas le relevé, le catalogue ou le registre SQLite. Il fonctionne avec la bibliothèque standard Python, indépendamment des noms de modèles de l'hôte. Utiliser ce bilan seulement si ses données sont accessibles et utiles à la mission.

## Constituer le relevé

Le coordinateur rassemble les tentatives réellement lancées et les résultats de revue ; RH analyse l'allocation et finance les coûts. Relever les identifiants dans les outils de session ou le [registre](supervision-locale.md), puis les mesures effectivement disponibles auprès de l'hôte. Le script ne recoupe pas automatiquement ces sources : leur fidélité reste à vérifier.

Conserver le fichier dans le dossier privé de la mission, par exemple `.orka/mesures.json` avec une exclusion Git adaptée au projet. Il peut contenir identités et références privées. Le script écrit son rapport JSON sur la sortie standard, sans créer de fichier de sa propre initiative :

```sh
python3 .agents/skills/orka/scripts/bilan_agents.py .orka/mesures.json
```

Adapter le chemin du script après installation. Exemple de **forme simulée, aucun agent exécuté** :

```json
{
  "version": 1,
  "mission": "exemple-simule",
  "couverture": "partielle",
  "tentatives": [
    {
      "tache": "T1",
      "tentative": 1,
      "agent_id": "simulation-agent-1",
      "role": "analyste-marche",
      "modele_applique": null,
      "effort_applique": null,
      "etat": "non_revu",
      "preuve": "Exemple simulé : résultat pas encore relu",
      "mesure": null,
      "cout": null
    }
  ]
}
```

Remplacer les valeurs simulées par les constats réels avant un bilan de mission. Une requête préparée ou une réservation sans agent lancé n'est pas une tentative mesurable dans ce relevé.

- `couverture` : `partielle` ou `complete_declaree` pour l'ensemble de la mission. Inclure le coordinateur si ses moyens sont couverts. La complétude est une déclaration ; le script ne peut détecter un agent oublié.
- Pour chaque tâche incluse, fournir toutes ses tentatives depuis 1, une seule ligne par numéro. Une tentative correspond au travail demandé jusqu'à sa première décision de revue ou son interruption. Une correction demandée après revue ouvre une nouvelle tentative, même si le même agent la réalise : conserver le constat `a_corriger` initial plutôt que le remplacer par `accepte`. Le même agent peut participer à plusieurs tentatives, dont les périodes doivent rester distinctes.
- `etat` : `accepte`, `a_corriger`, `non_revu` ou `interrompu`. `preuve` indique la revue et ses critères ou le constat d'absence de revue/interruption. Ce texte conserve la provenance ; le logiciel ne juge pas sa justesse métier. `accepte` décrit le résultat de cette tentative, pas une validation commerciale du projet.
- `modele_applique` et `effort_applique` : valeurs observées ou `null`/champs omis. Ne pas copier les paramètres demandés lorsqu'ils n'ont pas été confirmés. Le script ne contrôle pas la disponibilité des modèles ni l'identité des agents.
- `mesure` et `cout` : `null`/champs omis si indisponibles. Un zéro ne convient que pour une mesure réellement nulle.

## Ajouter les valeurs connues

Une mesure utilise exactement cette structure, avec des valeurs **illustratives** :

```json
{"id": "source-appel-ou-periode-unique", "source": "référence du compteur et période", "perimetre": "tentative_exclusive", "entree": 1200, "sortie": 300}
```

Normaliser les données avant de les inclure : un total propre à la tentative, hors consommation de ses enfants et sans chevauchement avec les autres lignes. Pour des instantanés cumulatifs, calculer un delta seulement si les bornes et remises à zéro sont connues ; sinon laisser la mesure absente. Documenter la transformation dans `source`. Entrée et sortie sont des entiers non négatifs. Les sous-comptes déjà inclus, comme cache ou raisonnement selon le fournisseur, ne sont pas à ajouter.

Le script refuse les identifiants de mesure dupliqués, les périmètres cumulatifs ou parents inclusifs et les champs supplémentaires. Deux identifiants différents peuvent néanmoins masquer un recouvrement : vérifier leur provenance. Pour une tentative encore active, une valeur provisoire reste partielle ; ne pas la présenter comme son coût final.

Un coût connu prend cette forme, avec un montant **simulé sans lien avec un tarif** :

```json
{"nature": "estime", "montant": "0.25", "devise": "EUR", "source": "référence du calcul, catégories et tarifs datés"}
```

`nature` distingue `constate` et `estime`. Un coût constaté exige une source couvrant cette seule tentative ; une facture globale n'est pas une ventilation par agent. Une estimation exige les hypothèses et tarifs applicables, sans inventer de prix. Utiliser un texte décimal non négatif, jusqu'à 18 chiffres entiers et 9 décimales. Pas de conversion de devises, de calcul tarifaire automatique, de montant négatif ni d'addition entre estimation et constat. Une éventuelle remise ou régularisation reste à traiter séparément. Une seule valeur de coût par tentative évite d'ajouter son estimation à son coût constaté.

## Lire le bilan

Le rapport conserve le détail par agent/tentative et calcule :

- Tâches, tentatives, reprises et états actuels des tâches. Les reprises sont les tentatives au-delà de la première, indépendamment du motif ; ce nombre seul n'est pas un score de qualité.
- Acceptation initiale : nombre de premières tentatives acceptées et nombre de premières tentatives réellement revues (`accepte` ou `a_corriger`). Les premières tentatives non revues ou interrompues sont exclues de ce dénominateur, même si une reprise réussit ensuite.
- Tokens connus en entrée, sortie et total ; nombres de tentatives mesurées et sans mesure. Sans mesure, les totaux sont `null`. Un total partiel reste un sous-total connu, même si les agents sont tous recensés.
- Coûts regroupés par nature et devise avec le nombre de tentatives renseignées, et nombre de tentatives sans coût. Une liste vide signifie indisponible, pas gratuit.

Ces résultats ne prouvent pas une supériorité de modèle. Comparer des tâches et critères semblables, expliquer les reprises et la couverture avant de proposer un changement de profil selon [l'évaluation](evaluation-agents.md). Aucun réglage, budget ou prompt n'est modifié automatiquement. Les [tests logiciels](../scripts/test_bilan_agents.py) utilisent uniquement des données simulées ; ils ne constituent pas une campagne d'agents réels.
