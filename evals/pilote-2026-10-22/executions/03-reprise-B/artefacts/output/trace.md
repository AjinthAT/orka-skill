# Trace factuelle

## Fichiers consultés

- `mandat-execution.txt`, `demande.txt`.
- `README.md`, `app.py`, `test_app.py`, `decisions.md`, `etat.md`, `positionnement.md`, `page.md` dans la cellule.
- Skill figé `skill-0.4.0/SKILL.md` et références `pilotage-missions.md`, `roles.md`, `workflows-entreprise.md`, `processus-transverses.md`, `gestion-documentaire.md`.
- `livrable.md` relu pour contrôle de longueur et des liens ; `README.md` et `etat.md` relus pour contrôle des liens.

## Corrections réalisées

- `app.py` : seuil `>= 5` remplacé par `> 7`, branche `None` préservée.
- `test_app.py` : six tests couvrant None, 4, 5, 7, 7.01 et 8.
- `README.md` : D2 et renvois au suivi.
- `etat.md` : D2 appliquée au prototype ; positionnement et page marqués à réexaminer, avec dépendance transitive et responsables proposés.
- Création de `livrable.md` et des captures demandées dans `output/`.

## Vérifications exécutées

- `python3 -B -m unittest -v` : six tests réussis, code de sortie 0.
- Empreintes SHA-256 avant et après : `decisions.md`, `positionnement.md` et `page.md` inchangés ; égalité également vérifiée par assertions.
- `livrable.md` : 241 mots selon découpage par espaces ; limite de 450 contrôlée par assertion.
- Existence de toutes les cibles locales des liens dans README, état et livrable contrôlée par assertions.
- Aucun autre agent lancé, aucune revue indépendante, aucun Web, aucune API externe, aucun déploiement, aucun registre créé.
