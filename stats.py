import plotly.express as px

def stats_prospection(df):
    total = len(df)
    contactes = df[df["Contacté ?"] == "Oui"]
    interet = contactes[contactes["Intérêt"].isin(["Vente envisagée", "Peut-être"])]
    taux = round(len(interet) / len(contactes) * 100, 2) if len(contactes) > 0 else 0
    return total, len(contactes), len(interet), taux

def graphique_interet(df):
    fig = px.histogram(df[df["Contacté ?"] == "Oui"], x="Intérêt", title="Répartition des intérêts")
    return fig
