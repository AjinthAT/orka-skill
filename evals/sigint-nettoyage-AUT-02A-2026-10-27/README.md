# Suspension pendant le nettoyage AUT-02A

Propriétaire : coordinateur de maintenance. Version documentaire : 1, 27 octobre 2026. Référence avant correction : `697d5a0`. État : correction et régressions vérifiées sur Linux/Python 3.14.3, sans appel modèle ni fusion. Les [premières corrections](../corrections-AUT-02A-2026-10-27/README.md) et les [captures initiales](../supervision-AUT-02A-2026-10-27/README.md) restent inchangées.

La sonde injecte un incident logiciel après lancement du travailleur fixe et le met en pause pour rendre le nettoyage observable. Elle envoie ensuite le **premier SIGINT réel** au contrôleur, pendant cette phase. Il ne s'agit ni d'un processus noyau bloqué ni d'un modèle.

| Preuve | Résultat |
|---|---|
| [Tests sur la référence](reference.log), [provenance](reference.json) | Les trois nouveaux tests échouent sur une copie temporaire de `697d5a0` avec le nouveau fichier de tests |
| [Vérification complète corrigée](verification.log) | 176 tests recensés : 135 réussis et 41 optionnels ignorés ; les 45 tests AUT-02A passent, dont les trois nouvelles régressions |
| [JSON de la sonde](stdout.json), [contrôle persistant](controle.json) | Sortie 2, état partiel, suspension persistée pendant le nettoyage ; aucune exception non capturée |
| [État après reprise sans levée](resume-sans-levee.json) | Mission toujours suspendue, T1 reste à une tentative, aucun nouveau lancement |
| [Registre exporté](registre-export.json), [journal du contrôleur](controleur.jsonl) | Réservation conservée ; l'arrêt physique confirmé du travailleur ne vaut pas libération implicite du registre |
| [Réception et empreintes du code](reception.json), [manifeste des captures](manifest.json) | Travailleur arrêté observé, code et tests identifiés par SHA256 ; zéro appel modèle |

Les deux autres variantes utilisent des SIGINT réels pendant la fermeture SQLite et des SIGINT répétés avec `wait`/`poll` simulés non confirmants. Elles vérifient la restauration du gestionnaire précédent, l'absence de succès fictif et de reçu d'arrêt inventé. Les signaux répétés ne recommencent pas les attentes.

Pour refaire les régressions sur des dossiers temporaires, depuis la racine du dépôt :

```sh
python -B -m unittest discover -s tests -p test_supervision_locale.py -k sigint_nettoyage -v
```

Le fichier `sonde.py` conserve l'entrée de la capture, pas une commande autonome à lancer sur une mission. Les copies sont consultables ; ne pas les rejouer ni les modifier. Le manifeste exclut cet index et lui-même. Les chemins bruts gardent leur provenance et ne constituent pas une base SQLite relocalisée. La qualification n'est pas étendue aux modèles, aux autres plateformes ou aux arrêts impossibles à confirmer.
