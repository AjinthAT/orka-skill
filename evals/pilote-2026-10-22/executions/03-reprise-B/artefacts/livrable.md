# Bilan de reprise du prototype

D2, décision actuelle de [decisions.md](decisions.md), est appliquée au prototype. La réalisation technique demandée est terminée ; le réexamen des documents métier reste ouvert.

## Modifications

- [app.py](app.py) déclenche « prioritaire » uniquement pour une attente strictement supérieure à 7 minutes. À 7 minutes, le résultat est « normale » ; pour `None`, il reste « inconnue ».
- [test_app.py](test_app.py) couvre l'attente inconnue, 4 minutes, l'ancien seuil de 5 minutes devenu normal, 7 minutes, 7,01 minutes et 8 minutes.
- [README.md](README.md) présente la règle D2 et la commande de vérification locale.
- [etat.md](etat.md) distingue la réalisation technique vérifiée des dépendances métier à réexaminer, avec responsables et ordre de reprise.

## Vérifications

La commande `python3 -B -m unittest -v` a exécuté six tests : tous réussis. Il s'agit d'un autocontrôle effectué par le même intervenant, sans revue indépendante ni délégation.

Les empreintes SHA-256 de `decisions.md`, `positionnement.md` et `page.md` ont été comparées avant et après intervention : elles sont identiques. L'historique D1/D2 est préservé. Aucun déploiement ni recherche externe n'a été effectué.

## Suites

Le [positionnement](positionnement.md) conserve une promesse fondée sur D1 ; la [page commerciale](page.md) en dépend et mentionne également l'ancien seuil. Ces fichiers sont inchangés et n'ont pas fait l'objet d'une nouvelle revue métier. Le marketing, avec le produit, devra réexaminer le positionnement selon D2, puis la rédaction pourra réexaminer la page à partir du positionnement retenu. Ces travaux ne sont pas exécutés dans cette reprise.
