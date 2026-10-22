D2 est appliquée au prototype : l’alerte est prioritaire uniquement au-delà de 7 minutes, normale à 7 minutes et inconnue lorsque l’attente vaut `None`.

Modifications réalisées :
- `app.py` applique le seuil strict de D2.
- `test_app.py` vérifie l’attente inconnue, les valeurs inférieures au seuil, le seuil exact et les valeurs supérieures.
- `README.md` décrit la règle actuelle et la commande de vérification.
- `etat.md` distingue le prototype actualisé des documents métier impactés qui nécessitent un réexamen séparé.

Vérifications : `python3 -B -m unittest -v` réussit : 4 tests, couvrant `None`, 0, 4, 5, 6.99, 7, 7.01 et 8 minutes. La comparaison des empreintes avant/après confirme que `decisions.md`, `positionnement.md` et `page.md` sont inchangés ; l’historique D1/D2 est préservé.

Suites : réexaminer séparément le positionnement, puis la page commerciale qui en dépend. Aucun document métier n’a été revérifié. Aucun déploiement ni recherche externe n’a été effectué.
