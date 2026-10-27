# Corrections de revue AUT-02A du 27 octobre 2026

Propriétaire : coordinateur de maintenance. Version documentaire : 1. Périmètre : trois défauts relevés sur `ce644e6`, puis leurs corrections dans la PR #3. État : corrections vérifiées sur Linux/Python 3.14.3. Aucun modèle ni fournisseur, aucune fusion, aucun redémarrage réel de la machine.

Les résultats initiaux dans [supervision-AUT-02A](../supervision-AUT-02A-2026-10-27/README.md) restent inchangés. Le [rapport de réception](../../docs/VALIDATION-AUT-02A.md) et le [guide](../../docs/SUPERVISEUR-LOCAL.md) décrivent les corrections et leurs limites.

Sept nouveaux tests portent sur la suspension pendant l'ouverture du registre, la provenance des échéances monotones et les arrêts non confirmés. Ils ont été exécutés séparément contre une copie temporaire de `ce644e6` contenant uniquement le nouveau fichier de tests en remplacement : les sept échouent sur cette référence. Les variantes de redémarrage d'horloge et d'attente non confirmée sont des injections logicielles ; l'interruption SQLite et les travailleurs Python sont réels.

| Preuve | Observation |
|---|---|
| [Référence avant corrections](avant.json), [journal](avant-complet.log) | Sept tests exécutés séparément sur la référence : six sorties 1 et une interruption non capturée (sortie -2) ; aucun ne passe |
| [Vérification globale après corrections](verification.log) | `python -B tools/verifier.py` : 173 tests recensés, 132 réussis et 41 optionnels ignorés ; les 42 tests AUT-02A, dont les sept régressions, passent |
| [Parcours nominal corrigé](nominal/stdout.json), [registre exporté](nominal/registre-export.json) | T1=2 tentatives, T2=1, total 115 recalculé, trois travailleurs logiciels et aucune réservation active |
| [Provenance](reception.json), [manifeste](manifest.json) | Empreintes du code et des tests examinés, plateforme et empreintes des captures brutes |

La variante de nettoyage incomplet vérifie aussi qu'un résultat de tâches complet ne peut masquer une incertitude finale de processus. L'injection d'attente non confirmée porte à la fois sur `wait` et `poll`, afin qu'aucune des deux interfaces n'atteste la fin. Les vrais enfants sont récoltés après retrait des doubles logiciels dans les tests ; un processus noyau réellement bloqué n'a pas été provoqué.

Les empreintes du manifeste excluent cet index et le manifeste lui-même. Les chemins absolus bruts identifient l'environnement d'origine et restent conservés tels quels. Les exports sont des preuves consultables, pas une base SQLite relocalisée. Il ne s'agit ni d'une comparaison de modèles ni d'une certification d'autres plateformes.
