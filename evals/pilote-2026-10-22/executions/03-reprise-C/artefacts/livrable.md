# Bilan de reprise du prototype

D2, décision actuelle de [decisions.md](decisions.md), est appliquée au prototype : l’alerte devient prioritaire uniquement lorsque l’attente dépasse strictement 7 minutes. Elle reste normale à 7 minutes et inconnue pour `None`, sans conversion en zéro.

Modifications réalisées :

- `app.py` utilise désormais la comparaison `> 7`.
- `test_app.py` couvre l’attente inconnue, zéro, l’ancien seuil de 5 minutes, les valeurs juste avant et après 7 minutes et le seuil exact.
- `README.md` décrit D2 et la commande de vérification locale.
- `etat.md` distingue le prototype actualisé des documents métier à réexaminer et précise les dépendances affectées.

Vérifications : `python3 -B -m unittest -v` a réussi les 6 tests. La comparaison des empreintes confirme que `decisions.md`, `positionnement.md` et `page.md` sont inchangés : D1 reste conservée comme historique. La revue QA distincte ne relève aucune anomalie ; le coordinateur accepte la version technique.

Suites : le positionnement doit être réexaminé séparément selon D2, puis la page commerciale qui en dépend. Leurs anciens messages à 5 minutes restent dans les fichiers historiques ; ils ne sont pas validés pour D2. Aucune nouvelle revue métier n’a été réalisée. Aucun déploiement ni recherche externe n’a été effectué.

**Prochain prompt à copier**

```text
Dans ce dossier de prototype, réexamine séparément positionnement.md selon D2, puis page.md à partir du positionnement révisé ; actualise etat.md et conserve l’historique de decisions.md, sans publication ni déploiement.
```
