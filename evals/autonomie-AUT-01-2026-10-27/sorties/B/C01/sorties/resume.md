# Bilan local — C01

Le total net retenu est **170**, sans devise attribuée : `120 + 80 + (-30) = 170`.

La [convention v2](../entrees/convention.md) précise que les montants sont déjà signés et que toutes les lignes, remboursements inclus, entrent dans la somme. Les trois lignes de [mouvements.csv](../entrees/mouvements.csv) sont donc conservées.

La [proposition production](../entrees/propositions.md) aboutit à 200 en ne gardant que les ventes ; elle est écartée car elle contredit cette convention. La proposition critique est retenue sur cette preuve, sans vote ni agent exécuté.

Le coordinateur assure la fonction de juge et la vérification en autocontrôle séquentiel ; aucune revue indépendante n'est revendiquée. Le mandat de [demande.txt](../demande.txt) délègue les choix de méthode et autorise l'écriture des deux livrables ainsi que le suivi local. Aucune décision humaine complémentaire n'est nécessaire.

Vérifications : trois lignes lues, somme recalculée, remboursement négatif inclus une seule fois, JSON relu avec un champ `total_net` numérique égal à 170. Les deux livrables sont terminés. Limite : la devise n'est pas fournie ; aucune validation de la réalité économique des mouvements au-delà des pièces locales.

Condition de réexamen : modification de la convention ou des mouvements. Aucune action restante dans le périmètre actuel.
