import streamlit as st
from datetime import datetime
import pandas as pd
from prospection import ajouter_entree, charger_donnees
from dvf import (
    get_communes_du_departement,
    get_sections,
    get_parcelles_geojson,
    get_mutations_by_id_parcelle,
    normaliser_mutations
)
from map import generer_carte_interactive
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

# 🔎 Carte interactive DVF
st.subheader("🗺️ Carte interactive DVF")

communes = get_communes_du_departement("69")
commune_nom_to_code = {c["nom"]: c["code"] for c in communes}
commune_default = "Lyon 3e Arrondissement" if "Lyon 3e Arrondissement" in commune_nom_to_code else sorted(commune_nom_to_code.keys())[0]
commune_choisie = st.selectbox("Commune", sorted(commune_nom_to_code.keys()), index=sorted(commune_nom_to_code.keys()).index(commune_default))
code_commune = commune_nom_to_code[commune_choisie]

sections = get_sections(code_commune)
parcelles = get_parcelles_geojson(code_commune)

m = generer_carte_interactive(sections, parcelles)
result = st_folium(m, width=700, height=500, returned_objects=["last_active_drawing"])

clicked = result.get("last_active_drawing", {}).get("properties", {})
clicked_id = clicked.get("id", "")
clicked_type = clicked.get("type", "")

if clicked_type == "section":
    st.subheader(f"📍 Parcelles de la section {clicked_id}")
    parcelles_section = [p for p in parcelles if p["id"][5:10] == clicked_id]
    st.write(f"{len(parcelles_section)} parcelles trouvées.")
elif clicked_type == "parcelle":
    st.subheader(f"📑 Mutations de la parcelle {clicked_id}")
    mutations = get_mutations_by_id_parcelle(clicked_id)
    if not mutations:
        st.warning("❌ Aucune mutation DVF trouvée pour cette parcelle.")
    else:
        df_mutations = normaliser_mutations(mutations)
        df_mutations["Date mutation"] = df_mutations["Date mutation"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_mutations)

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
