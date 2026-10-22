# Prototype fictif

Selon D2, décision actuelle de simulation, une table passe en priorité lorsque l’attente est strictement supérieure à 7 minutes. À 7 minutes et en dessous, elle reste normale. Une attente absente (`None`) reste inconnue, sans conversion en zéro. L’ancien seuil de 5 minutes ne déclenche plus de priorité.

Cette règle est une décision de simulation, pas une norme sectorielle. L’historique des décisions est conservé dans `decisions.md`.

Vérification locale : `python3 -B -m unittest -v`. Les tests couvrent `None`, zéro, l’ancien seuil de 5 minutes, la frontière de 7 minutes et son dépassement.
