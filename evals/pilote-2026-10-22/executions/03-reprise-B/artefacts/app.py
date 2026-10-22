def priorite(attente_minutes):
    if attente_minutes is None:
        return "inconnue"
    return "prioritaire" if attente_minutes > 7 else "normale"
