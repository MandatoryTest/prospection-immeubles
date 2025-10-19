import streamlit as st
from datetime import datetime
from prospection import ajouter_entree, charger_donnees
from dvf import get_mutations, get_parcelles_geojson, get_mutations_by_parcelle
from map import generer_carte, generer_carte_parcelles
from stats import stats_prospection, graphique_interet
from export import generer_pdf
from streamlit_folium import st_folium

st.set_page_config(page_title="Prospection immobilière", layout="wide")
st.title("🏢 Prospection immobilière + DVF")

# 📋 Saisie d'un contact immeuble
with st.form("ajout_contact"):
    st.subheader("Ajouter un contact immeuble")
    col1, col2 = st.columns(2)
    with col1:
        immeuble = st.text_input("Immeuble")
        adresse = st.text_input("Adresse")
        etage = st.text_input("Étage")
        nom = st.text_input("Nom affiché")
        type_bien = st.selectbox("Type de bien", ["T1", "T2", "T3", "Maison", "Inconnu"])
    with col2:
        contacte = st.radio("Contacté ?", ["Oui", "Non"])
        interet = st.selectbox("Intérêt", ["Vente envisagée", "Location", "Non", "Peut-être", "Inconnu"])
        action = st.text_input("Action à suivre")
        relance = st.date_input("Date de relance", value=None)
        commentaire = st.text_area("Commentaire")

    submitted = st.form_submit_button("Ajouter")
    if submitted:
        data = {
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Immeuble": immeuble,
            "Adresse": adresse,
            "Étage": etage,
            "Nom affiché": nom,
            "Type de bien": type_bien,
            "Contacté ?": contacte,
            "Intérêt": interet,
            "Action": action,
            "Relance": relance.strftime("%Y-%m-%d") if relance else "",
            "Commentaire": commentaire
        }
        ajouter_entree(data)
        st.success(f"✅ Contact {nom} ajouté.")

# 📌 Suivi des immeubles
st.subheader("Suivi des immeubles")
df = charger_donnees()
filtre = st.selectbox("Filtrer par immeuble", ["Tous"] + sorted(df["Immeuble"].unique()))
if filtre != "Tous":
    df = df[df["Immeuble"] == filtre]
st.dataframe(df)

# 🔔 Relances à venir
st.subheader("Relances à venir")
aujourd_hui = datetime.today().strftime("%Y-%m-%d")
relances = df[df["Relance"] >= aujourd_hui]
st.dataframe(relances)

# 📊 Statistiques
st.subheader("Statistiques de prospection")
total, contactes, interet, taux = stats_prospection(df)
st.metric("Total entrées", total)
st.metric("Contactés", contactes)
st.metric("Intéressés", interet)
st.metric("Taux de conversion", f"{taux}%")
st.plotly_chart(graphique_interet(df))

# 🔍 Mutations DVF par section
st.subheader("Mutations DVF par section cadastrale")
code_commune = st.text_input("Code INSEE commune", value="69381")
section = st.text_input("Section cadastrale", value="000A")
date_min = st.date_input("Date minimale", value=datetime(2022, 1, 1))
date_max = st.date_input("Date maximale", value=datetime(2025, 12, 31))

if st.button("Rechercher les mutations DVF"):
    mutations = get_mutations(code_commune, section)
    if isinstance(mutations, list):
        filtrées = [
            m for m in mutations
            if date_min.strftime("%Y-%m-%d") <= m["date_mutation"] <= date_max.strftime("%Y-%m-%d")
        ]
        st.success(f"{len(filtrées)} mutations trouvées")
        st.dataframe(filtrées)
    else:
        st.error(mutations.get("error", "Erreur inconnue"))

# 🗺️ Carte des parcelles + sélection
st.subheader("Carte des parcelles cadastrales")
geojson = get_parcelles_geojson(code_commune)
if "features" in geojson:
    parcelles = [f["id"] for f in geojson["features"]]
    parcelle_choisie = st.selectbox("Choisir une parcelle", parcelles)
    if parcelle_choisie:
        mutations_parcelle = get_mutations_by_parcelle(parcelle_choisie)
        if isinstance(mutations_parcelle, list):
            st.success(f"{len(mutations_parcelle)} mutations pour {parcelle_choisie}")
            st.dataframe(mutations_parcelle)
        else:
            st.error(mutations_parcelle.get("error", "Erreur inconnue"))
    m = generer_carte_parcelles(geojson)
    st_folium(m, width=700, height=500)
else:
    st.error("Impossible de charger les parcelles")

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
