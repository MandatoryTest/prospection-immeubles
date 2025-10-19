<<<<<<< HEAD
import pandas as pd
from datetime import datetime

FILENAME = "suivi_prospection.csv"

def charger_donnees():
    try:
        return pd.read_csv(FILENAME)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Date", "Immeuble", "Adresse", "Étage", "Nom affiché", "Type de bien",
            "Contacté ?", "Intérêt", "Action", "Relance", "Commentaire"
        ])

def ajouter_entree(data):
    df = charger_donnees()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILENAME, index=False)
    return df
=======
import pandas as pd
from datetime import datetime

FILENAME = "suivi_prospection.csv"

def charger_donnees():
    try:
        return pd.read_csv(FILENAME)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Date", "Immeuble", "Adresse", "Étage", "Nom affiché", "Type de bien",
            "Contacté ?", "Intérêt", "Action", "Relance", "Commentaire"
        ])

def ajouter_entree(data):
    df = charger_donnees()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILENAME, index=False)
    return df
>>>>>>> 36d8982681a72f0a9e769e0284b39d72e49652b3
