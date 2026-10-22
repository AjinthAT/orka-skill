# Prototype fictif

Version de reprise : D2, décision actuelle définie dans [decisions.md](decisions.md#d2--actuelle-remplace-d1).

Une table passe en priorité lorsque son attente est strictement supérieure à 7 minutes. À 7 minutes, elle reste normale. Une attente absente (`None`) reste inconnue.

Vérification locale : `python3 -B -m unittest -v`.

Les documents métier impactés et leur réexamen restant à faire sont suivis dans [etat.md](etat.md).
