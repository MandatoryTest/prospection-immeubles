import streamlit as st
from datetime import datetime
from prospection import ajouter_entree, charger_donnees
from dvf import (
    get_communes_du_departement,
    get_sections,
    get_parcelles_from_mutations,
    get_mutations_by_parcelle
)
from map import generer_carte_mutations
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

# 🔎 Exploration DVF ciblée
st.subheader("Exploration DVF par commune, section et parcelle")

communes = get_communes_du_departement("69")
commune_nom_to_code = {c["nom"]: c["code"] for c in communes}
commune_choisie = st.selectbox("Commune", sorted(commune_nom_to_code.keys()))
code_commune = commune_nom_to_code[commune_choisie]

sections = get_sections(code_commune)
section_choisie = st.selectbox("Section cadastrale", sections)

parcelles = get_parcelles_from_mutations(code_commune, section_choisie)
parcelle_choisie = st.selectbox("Parcelle", parcelles)

if st.button("Afficher mutations et carte"):
    mutations = get_mutations_by_parcelle(code_commune, section_choisie, parcelle_choisie)
    st.success(f"{len(mutations)} mutations pour {parcelle_choisie}")
    st.dataframe(mutations)
    m = generer_carte_mutations(mutations)
    st_folium(m, width=700, height=500)

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
