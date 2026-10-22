# P1 — Production backend

D2 est appliquée dans `app.py` : `prioritaire` uniquement au-delà de 7 minutes, `normale` à 7 minutes et en dessous, `inconnue` pour `None`, sans conversion en zéro.

Fichiers modifiés : `app.py`, `test_app.py`, `README.md`. Le présent bilan est créé dans `output/specialistes/P1-production.md`.

Vérification exécutée : `python3 -B -m unittest -v` ; résultat : 6 tests réussis, code de sortie 0. Couverture : `None`, zéro, 4, 5, 5.1, 6, 6.999, 7, 7.001 et 8 minutes. L’ancien seuil de 5 minutes reste normal ; le passage en priorité exige strictement plus de 7 minutes.

Les empreintes des 7 fichiers existants hors périmètre sont inchangées, dont `decisions.md`, `etat.md`, `positionnement.md` et `page.md`. Aucun déploiement ni recherche externe.

Limites et suites : les documents métier n’ont pas été réexaminés. Le coordinateur prend en charge `etat.md` et `livrable.md` ; une revue QA distincte puis son acceptation restent nécessaires.
