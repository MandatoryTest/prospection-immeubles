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
from map import generer_carte_complete
from stats import stats_prospection, graphique_interet
from export import generer_pdf
from streamlit_folium import st_folium

if "afficher_mutations" not in st.session_state:
    st.session_state.afficher_mutations = False

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
commune_default = "Lyon 3e Arrondissement"
commune_names = sorted(commune_nom_to_code.keys())
default_index = commune_names.index(commune_default) if commune_default in commune_names else 0
commune_choisie = st.selectbox("Commune", commune_names, index=default_index)
code_commune = commune_nom_to_code[commune_choisie]

section_features = get_sections(code_commune)
section_codes = [s["properties"]["code"] for s in section_features]
section_choisie = st.selectbox("Section cadastrale", section_codes)
code_section = section_choisie.zfill(5)
section_geo = [s for s in section_features if s["properties"]["code"] == section_choisie]

parcelles = get_parcelles_geojson(code_commune)
parcelles_section = [p for p in parcelles if p["id"][5:10] == code_section]
parcelle_ids = [p["id"] for p in parcelles_section]
parcelle_choisie = st.selectbox("Parcelle", parcelle_ids)
parcelle_geo = next((p for p in parcelles_section if p["id"] == parcelle_choisie), None)

# 🗺️ Carte 1 : parcelles de la section
m = generer_carte_complete(section_features, parcelles_section, [], set())
st.subheader("🗺️ Carte cadastrale")
st_folium(m, width=700, height=500, returned_objects=[])

# 📑 Mutations
if st.button("Afficher mutations"):
    st.session_state.afficher_mutations = True
    st.session_state.parcelle_choisie = parcelle_choisie

if st.session_state.afficher_mutations:
    mutations = get_mutations_by_id_parcelle(st.session_state.parcelle_choisie)
    if not mutations:
        st.warning("❌ Aucune mutation DVF trouvée pour cette parcelle.")
    else:
        df_mutations = normaliser_mutations(mutations)
        df_mutations["Date mutation"] = df_mutations["Date mutation"].dt.strftime("%d/%m/%Y")
        st.subheader("Mutations DVF")
        st.dataframe(df_mutations)

        mutation_points = []
        parcelles_mutées = set()
        for m in mutations:
            for i in m.get("infos", []):
                mutation_points.append({
                    "latitude": i.get("latitude"),
                    "longitude": i.get("longitude"),
                    "valeur_fonciere": i.get("valeur_fonciere"),
                    "type_local": i.get("type_local")
                })
                parcelles_mutées.add(i.get("id_parcelle"))

        # 🗺️ Carte 2 : mutations sur la section
        m = generer_carte_complete(section_features, parcelles_section, mutation_points, parcelles_mutées)
        st.subheader("🗺️ Carte avec mutations")
        st_folium(m, width=700, height=500, returned_objects=[])

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
