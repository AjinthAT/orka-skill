# Réception logicielle AUT-02A du 27 octobre 2026

Propriétaire : coordinateur de maintenance. Version documentaire : 1. État : captures de trois parcours exécutés, sans modèle. Source : [superviseur facultatif](../../tools/supervision_locale/controleur.py), basé sur AUT-01 `a9d4a11`, avec empreintes du code exact dans chaque `mission.json`. Le [rapport de réception](../../docs/VALIDATION-AUT-02A.md) distingue cette preuve logicielle des capacités futures.

| Cas | Capture du résultat | Résultat observé |
|---|---|---|
| Nominal | [stdout JSON](nominal/stdout.json), [registre exporté](nominal/registre-export.json) | Succès ; T1 deux tentatives, T2 une ; total 115 vérifié et trois travailleurs |
| Sortie fausse, code 0 | [stdout JSON](mauvais-total/stdout.json), [registre exporté](mauvais-total/registre-export.json) | Partiel, T1 bloquée après une tentative ; aucune sortie canonique, T2 non lancée |
| Crash après publication | [état avant reprise](crash-publication/avant-reprise.json), [résultat après reprise](crash-publication/stdout.json) | Contrôleur sorti volontairement avec code 89 après publication T1, avant soumission ; reprise sur même base et succès, toujours trois travailleurs |

Les sous-dossiers contiennent les entrées, sorties de tentative, sorties canoniques, requêtes, identités, reçus d'arrêt et journaux bruts copiés après exécution. `execution.json` conserve la commande et le code de sortie. `registre-export.json` est un export en lecture seule des états, événements et tentatives, sans duplication d'autorité pendant l'exécution. Aucun modèle, coût ou paramètre réellement appliqué à un modèle n'est inventé.

Le [journal de vérification](verification.log) recense 166 tests : 125 réussis, 41 optionnels ignorés, dont 35 nouveaux tests AUT-02A réussis sur Linux. Les suites de crash supplémentaires créent des dossiers temporaires ; leurs sorties ne sont pas assimilées à des évaluations d'IA. Le paquet portable et la version 0.9.0 sont vérifiés.

Le [manifeste](manifest.json) conserve les empreintes des captures et du journal de test. Il exclut son propre fichier et cet index. Les chemins absolus bruts désignent l'environnement d'origine ; les fichiers ont été conservés tels quels. Les copies sont consultables, mais ne constituent pas une base SQLite relocalisée ou une sauvegarde de mission exécutable. Refaire une recette exige une destination neuve ; ne pas rejouer ni modifier ces captures.

Qualification initiale : Linux x86_64, Python 3.14.3, stockage local et travailleurs fixes sans descendants. Aucun verdict sur un modèle, un juge IA, un environnement hostile, d'autres systèmes, le CLI Codex ou L4.
