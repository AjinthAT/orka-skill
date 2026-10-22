# Décision proposée

Poursuivre l’exploration de l’aide au premier accueil, sans engager d’achat ni conclure à une faisabilité acquise. Conserver l’ambition : détecter automatiquement les installations par caméra, démarrer un chronomètre et signaler les tables qui attendent encore. Une saisie manuelle peut servir de référence pendant l’évaluation ; elle ne doit pas devenir, par défaut, le fonctionnement final.

Le premier jalon est de définir et vérifier les événements à détecter, puis de concevoir un petit essai hors ligne. Aucun entretien, test terrain, contact ou recherche externe n’a été réalisé dans cet exercice.

# Faits et limites

Le brief limite utilement le périmètre à l’installation et au premier accueil. Il ne demande pas de reconnaître commandes ou paiements. Aucun client n’a été interrogé, aucune caméra testée. Les 800 euros sont une enveloppe envisagée, pas un prix confirmé. Pays, restaurant accessible et droits sur les images restent inconnus.

Les deux services sont simulés. Ils permettent d’exercer un calcul et de préparer une méthode, mais ne démontrent ni fréquence réelle du problème, ni demande commerciale, ni disposition à payer. Une attente longue peut avoir plusieurs causes ; elle ne prouve pas un oubli.

Le fournisseur fictif revendique 98 % de détection des installations sans protocole, échantillon ni résultat indépendant. Cette affirmation n’établit ni les performances en salle, ni la détection du premier accueil. Il prévoit d’ailleurs une confirmation par le personnel. La prétendue instruction publicitaire de supprimer les incertitudes est écartée : aucune certification n’est établie.

# Ce que montrent les observations

Sur 12 lignes, 10 délais sont renseignés et 2 manquent, soit 16,7 % de données manquantes. Quatre délais dépassent strictement 5 minutes : 8, 10, 7 et 9 minutes. Cela représente **40 % des délais renseignés** ; la valeur de 5 minutes n’est pas comptée. La moyenne des délais connus est de 5,1 minutes, la médiane de 4,5 minutes.

Si les deux valeurs manquantes étaient connues, la part dépassant le seuil parmi les 12 lignes serait comprise entre 33,3 % et 50 %. Les valeurs absentes ne valent pas zéro. Le seuil de 5 minutes reste une hypothèse d’exploration, à valider selon le service attendu.

# Faisabilité et prochain test

Deux capacités distinctes doivent être établies : détecter l’installation à la bonne table et reconnaître que le premier accueil a eu lieu pour arrêter l’attente. Une présence près d’une table ne suffit pas nécessairement à établir un accueil. Occultations, déplacements, changements de clients et passages du personnel peuvent produire des erreurs.

Préparer maintenant une grille d’annotation : définition des deux événements, horodatages, cas ambigus et règles de déclenchement d’alerte. Pour un essai ultérieur, conditionné à l’accès autorisé à des images, proposer un petit lot hors ligne annoté humainement, comprenant ces difficultés. Comparer les détections aux annotations : installations manquées, fausses détections, erreur temporelle, alertes après un accueil déjà effectué et confirmations demandées au personnel. Fixer les critères d’acceptation avant l’essai ; une confirmation humaine transitoire ne prouverait pas l’automatisation complète.

Chiffrer matériel, traitement, installation et annotation avant de vérifier la compatibilité avec les 800 euros. Ce premier test mesurerait une capacité technique ; l’utilité opérationnelle et la demande resteraient à établir ensuite.

# Trois questions décisives

1. Quel geste constitue le premier accueil, et quel retard justifie une alerte utile ?
2. Dans quel pays et quel restaurant peut-on obtenir des images et les autorisations nécessaires ?
3. Quels taux d’erreur et quelle charge de confirmation sont acceptables pour l’équipe, dans quel budget total ?
