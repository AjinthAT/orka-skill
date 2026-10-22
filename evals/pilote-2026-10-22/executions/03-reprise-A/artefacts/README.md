# Prototype fictif

Règle actuelle de simulation : D2, qui remplace D1 (voir `decisions.md`). Une alerte devient prioritaire lorsque l’attente est strictement supérieure à 7 minutes. À 7 minutes et en dessous, elle reste normale. Une attente valant `None` reste inconnue.

Vérification locale : `python3 -B -m unittest -v`.
