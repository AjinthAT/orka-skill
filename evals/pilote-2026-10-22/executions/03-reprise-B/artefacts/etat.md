# État simulé après reprise — v2, 22 octobre 2026

Responsable du suivi : coordinateur. Source du changement : instruction de reprise et [D2, décision actuelle](decisions.md#d2--actuelle-remplace-d1). D1 reste conservée dans [l'historique](decisions.md#d1--historique-remplacee).

| Élément | État actuel | Référence et impact | Prochain responsable / action |
|---|---|---|---|
| Règle produit | D2 appliquée au prototype | D2 remplace D1 : attente > 7, à 7 normale, None inconnue | Produit : conserver D2 comme référence |
| [Prototype](app.py), [tests](test_app.py) et [notice](README.md) | Reprise D2 terminée et autocontrôlée localement | 6 tests réussis avec `python3 -B -m unittest -v` | Technique : résultat livré, voir [bilan](livrable.md) |
| [Positionnement](positionnement.md) | À réexaminer ; fichier inchangé, version historique fondée sur D1 | Impact direct du changement de règle produit : promesse de priorité dès 5 minutes devenue incompatible avec D2 | Marketing avec produit : réexaminer séparément sur D2 |
| [Page commerciale](page.md) | À réexaminer ; fichier inchangé, version historique fondée sur l'ancien positionnement | Impact transitif via le positionnement ; le message « dès 5 minutes » dépend de D1 | Rédaction avec marketing : réexaminer séparément après le positionnement |

Aucune nouvelle revue métier du positionnement ou de la page commerciale n'a été effectuée. Leur ancien état « terminé selon D1 » ne vaut pas validation sous D2. Les suites métier restent ouvertes ; aucun déploiement n'a eu lieu.
