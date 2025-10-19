import streamlit as st
from datetime import datetime
from prospection import ajouter_entree, charger_donnees
from dvf import (
    get_mutations,
    get_mutations_by_parcelle,
    get_parcelles_from_mutations,
    get_communes_du_departement,
    get_sections_geojson
)
from map import generer_carte_parcelles
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

# 🔎 Exploration DVF par section cadastrale
st.subheader("Exploration DVF par section cadastrale")

code_commune = st.text_input("Code INSEE commune", value="69383")
section = st.text_input("Code section cadastrale (ex: AC)", value="AC")
section_code = section.zfill(5)

# 📍 Parcelles extraites depuis mutations DVF
parcelles = get_parcelles_from_mutations(code_commune, section_code)
if parcelles:
    parcelle_choisie = st.selectbox("Parcelle", parcelles)

    if st.button("Afficher mutations pour cette parcelle"):
        mutations = get_mutations(code_commune, section_code)
        mutations_parcelle = [
            m for m in mutations
            if parcelle_choisie in [p["id_parcelle"] for p in m.get("parcelles", [])]
        ]
        st.success(f"{len(mutations_parcelle)} mutations trouvées pour {parcelle_choisie}")
        st.dataframe(mutations_parcelle)

        # Carte centrée sur la parcelle
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"id": parcelle_choisie},
                "geometry": {
                    "type": "Point",
                    "coordinates": [m["longitude"], m["latitude"]]
                }
            } for m in mutations_parcelle if "longitude" in m and "latitude" in m]
        }
        if geojson["features"]:
            m = generer_carte_parcelles(geojson)
            st_folium(m, width=700, height=500)
        else:
            st.warning("Coordonnées géographiques non disponibles pour affichage cartographique.")
else:
    st.warning("Aucune parcelle trouvée pour cette section.")

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
