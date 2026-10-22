# État de reprise — D2

Propriétaire du suivi : coordinateur. Version de reprise : D2. Source de la règle actuelle : [decisions.md](decisions.md#d2--actuelle-remplace-d1). D1 reste conservée comme historique.

| Élément | État actuel | Dépendance et suite |
|---|---|---|
| Règle produit | D2 actuelle ; seuil strictement supérieur à 7 minutes, normale à 7, inconnue pour `None` | Décision de simulation, remplace D1 |
| Prototype (`app.py`, `test_app.py`, `README.md`) | D2 appliquée ; 6 tests locaux réussis, revue QA distincte sans correction, acceptation du coordinateur | Vérifications techniques terminées selon D2 |
| [Positionnement](positionnement.md) | À réexaminer ; version historique D1 inchangée | Impact direct du changement de règle : promesse à 5 minutes devenue périmée. Responsable de la reprise proposée : produit et marketing |
| [Page commerciale](page.md) | À réexaminer ; version historique inchangée | Impact indirect : dépend du positionnement reposant sur D1 et annonce encore 5 minutes. Réexaminer après le positionnement ; responsable proposé : marketing |

Aucune nouvelle revue métier du positionnement ou de la page commerciale n'a été réalisée. Leur ancien état « terminé » ne vaut pas validation selon D2. Leur réexamen séparé reste à faire ; aucune publication ni aucun déploiement n'a lieu dans cette reprise.
