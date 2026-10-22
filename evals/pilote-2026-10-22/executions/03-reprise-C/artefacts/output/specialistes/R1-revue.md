# R1 — Revue QA de la reprise D2

Revue technique et documentaire locale, réalisée le 22 octobre 2026. Avis : critères du mandat satisfaits ; acceptation finale réservée au coordinateur. Aucune correction demandée.

## Critères satisfaits

- `app.py` traite explicitement `None` avant toute comparaison et renvoie `inconnue`. Aucune conversion en zéro. Pour une attente numérique, le résultat est `prioritaire` uniquement si elle est strictement supérieure à 7 ; à 7 et en dessous, il est `normale`.
- Les tests couvrent `None`, zéro, 4, l'ancien seuil 5, 5.1, 6, 6.999, 7, 7.001 et 8. Ils vérifient notamment l'abandon du seuil D1, la frontière exacte D2 et les deux côtés de cette frontière.
- `README.md` décrit ces comportements et qualifie D2 de décision de simulation ; la commande de vérification est exacte.
- `etat.md` marque séparément `positionnement.md` et `page.md` à réexaminer. Il explicite l'impact direct sur le positionnement puis l'impact indirect sur la page qui en dépend, avec reprise de la page après le positionnement. Il ne prétend pas à une nouvelle revue métier et retire toute valeur de validation D2 à l'ancien état « terminé ».
- Les trois fichiers protégés ont les mêmes empreintes SHA-256 que dans `output/empreintes-initiales.json`. L'historique D1 et la décision actuelle D2 de `decisions.md` sont préservés.
- `livrable.md` est factuel, en français et compte 223 mots selon un découpage sur les espaces, donc moins de 450. Il décrit les modifications, les tests et les suites. Sa mention de revue technique en attente est cohérente avec sa version soumise à cette revue ; le coordinateur pourra l'actualiser après acceptation.

## Preuves reproductibles

Depuis la racine de cette cellule :

```sh
python3 -B -m unittest -v
```

Résultat observé : 6 tests réussis, `OK`, code de sortie 0.

```sh
python3 -B - <<'PY'
import hashlib, json
from pathlib import Path
initial = json.loads(Path('output/empreintes-initiales.json').read_text())
for name in ('decisions.md', 'positionnement.md', 'page.md'):
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    print(name, actual, actual == initial[name])
print('mots du bilan :', len(Path('livrable.md').read_text().split()))
PY
```

Résultats observés : trois comparaisons `True`, 223 mots.

| Fichier protégé | Empreinte SHA-256 observée |
|---|---|
| `decisions.md` | `247c8853dd57bb15c0001deaad5773b21b647cd302d24cad1694c142cc5307f3` |
| `positionnement.md` | `3102514976e5ed7bdeead8ffdc3f9918f7b3b0063781afcfe1528c0cb1424833` |
| `page.md` | `7a860e59f0c7f18f079bb4d67bd49f29828248146d781a2175ea8e5dbe58502f` |

## Critères non satisfaits et limites

Aucun critère non satisfait ni anomalie technique relevée dans le périmètre demandé. Le rapport P1 est cohérent avec les résultats réexécutés ; son constat d'`etat.md` inchangé correspond à son étape de production, avant le suivi du coordinateur.

Non vérifiés : pertinence métier, contenu commercial et validité sectorielle de `positionnement.md` et `page.md`. Leurs empreintes prouvent leur préservation, pas une validation métier. Les entrées hors contrat de cette simulation ne sont pas évaluées. Aucun Web, service externe ni déploiement utilisé pour cette revue. Seul `output/specialistes/R1-revue.md` a été écrit par le relecteur.

Écart d'exécution du relecteur : au démarrage, lecture du skill Orka dans le dépôt d'instructions, hors cellule, malgré la restriction de lecture du mandat. Cette lecture n'a entraîné aucune modification hors cellule ; elle ne constitue pas une preuve de conformité du périmètre d'accès. Les vérifications fonctionnelles ci-dessus restent reproductibles dans la cellule.
