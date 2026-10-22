# Lecture manuelle de la simulation

Propriétaire : coordinateur de maintenance. Version : 1, 22 octobre 2026. Autocontrôle documentaire, sans nouvel agent. La matrice et le bilan JSON déjà produits sont lus comme du texte ; aucun Python n’est exécuté pour ce comptage manuel. Cela ne qualifie pas un hôte physiquement dépourvu de Python.

Les six lignes de la [matrice](README.md) se répartissent ainsi : trois terminées, une interrompue, une hors protocole et une encore préparée. Parmi les trois terminées, deux sont évaluables (un succès et un échec) et la troisième reste inconclusive, faute de revue indispensable. Cela donne cinq observations fabriquées reçues et zéro exécution réelle.

| Compte manuel | Valeur | Lecture |
|---|---|---|
| Prévu | 6 | Toutes les lignes de la matrice |
| Reçu | 5 | Une ligne reste préparée |
| Évaluable | 2 | Un succès + un échec |
| Succès / évaluables | 1/2 | Ne couvre pas les quatre autres issues |
| Succès / prévus | 1/6 | Ne transforme pas les absences en échecs connus |
| Inconclusif | 1 | La revue manquante n’est pas une approbation |
| Interrompu / hors protocole | 1 / 1 | Conservés, exclus du taux comparable |

Le résultat attendu de 20 × 6 est 120, et la marge sur 150 est 30. Le total fourni de 121 dans e0002 ne respecte pas ce contrôle. La ligne e0004 peut contenir ces nombres corrects mais reste hors protocole ; elle n’est pas ajoutée aux succès comparables.

Une seule ligne porte des tokens fabriqués, ce qui ne couvre pas les cinq observations. L’estimation de 0,25 EUR et le montant étiqueté constaté de 0,10 USD sont tous deux simulés et ne s’additionnent pas. La durée illustrative de 9,5 secondes est murale. Réglages appliqués inconnus et couverture de traces déclarée restent des limites.

Ce comptage correspond au [bilan conservé](bilan.json). Il illustre la procédure manuelle ; il ne constitue ni une campagne de modèles, ni une revue indépendante, ni un résultat économique.
