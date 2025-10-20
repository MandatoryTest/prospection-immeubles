import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
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
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Prospection immobilière", layout="wide")
st.title("🏢 Prospection immobilière + DVF")

# 📋 Ajout de contact
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
            "Commentaire": commentaire,
            "ID": str(uuid.uuid4())
        }
        ajouter_entree(data)
        st.success(f"✅ Contact {nom} ajouté.")

# 📌 Tableau interactif
st.subheader("Suivi des immeubles")
df = charger_donnees()
filtre = st.selectbox("Filtrer par immeuble", ["Tous"] + sorted(df["Immeuble"].unique()))
if filtre != "Tous":
    df = df[df["Immeuble"] == filtre]

if df.empty:
    st.info("Aucune entrée trouvée.")
else:
    df_actions = df.copy()
    df_actions["Actions"] = ["✏️ Modifier / 🗑️ Supprimer"] * len(df)

    gb = GridOptionsBuilder.from_dataframe(df_actions)
    gb.configure_column("Actions", editable=False)
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df_actions,
        gridOptions=grid_options,
        update_on="selection_changed",
        height=400,
        fit_columns_on_grid_load=True
    )

    selected = grid_response.get("selected_rows", [])
    if selected:
        selected_id = selected[0]["ID"]
        selected_row = df[df["ID"] == selected_id].iloc[0]

        with st.form("modifier_contact"):
            col1, col2 = st.columns(2)
            with col1:
                immeuble = st.text_input("Immeuble", value=selected_row["Immeuble"])
                adresse = st.text_input("Adresse", value=selected_row["Adresse"])
                etage = st.text_input("Étage", value=selected_row["Étage"])
                nom = st.text_input("Nom affiché", value=selected_row["Nom affiché"])
                type_bien = st.selectbox("Type de bien", ["T1", "T2", "T3", "Maison", "Inconnu"], index=["T1", "T2", "T3", "Maison", "Inconnu"].index(selected_row["Type de bien"]))
            with col2:
                contacte = st.radio("Contacté ?", ["Oui", "Non"], index=["Oui", "Non"].index(selected_row["Contacté ?"]))
                interet = st.selectbox("Intérêt", ["Vente envisagée", "Location", "Non", "Peut-être", "Inconnu"], index=["Vente envisagée", "Location", "Non", "Peut-être", "Inconnu"].index(selected_row["Intérêt"]))
                action = st.text_input("Action à suivre", value=selected_row["Action"])
                relance = st.date_input("Date de relance", value=pd.to_datetime(selected_row["Relance"]) if selected_row["Relance"] else None)
                commentaire = st.text_area("Commentaire", value=selected_row["Commentaire"])

            col_modif, col_suppr = st.columns(2)
            with col_modif:
                modif = st.form_submit_button("💾 Enregistrer les modifications")
            with col_suppr:
                suppr = st.form_submit_button("🗑️ Supprimer ce contact")

            if modif:
                df.loc[df["ID"] == selected_id, :] = {
                    "Date": selected_row["Date"],
                    "Immeuble": immeuble,
                    "Adresse": adresse,
                    "Étage": etage,
                    "Nom affiché": nom,
                    "Type de bien": type_bien,
                    "Contacté ?": contacte,
                    "Intérêt": interet,
                    "Action": action,
                    "Relance": relance.strftime("%Y-%m-%d") if relance else "",
                    "Commentaire": commentaire,
                    "ID": selected_id
                }
                df.to_csv("prospection.csv", index=False)
                st.success("✅ Modifications enregistrées.")
                st.experimental_rerun()

            if suppr:
                df = df[df["ID"] != selected_id]
                df.to_csv("prospection.csv", index=False)
                st.success("❌ Contact supprimé.")
                st.experimental_rerun()

# 🔔 Relances
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

# 🗺️ Carte DVF
st.subheader("Carte DVF : mutations par parcelle")
communes = get_communes_du_departement("69")
commune_nom_to_code = {c["nom"]: c["code"] for c in communes}
commune_default = "Lyon 3e Arrondissement" if "Lyon 3e Arrondissement" in commune_nom_to_code else sorted(commune_nom_to_code.keys())[0]
commune_choisie = st.selectbox("Commune", sorted(commune_nom_to_code.keys()), index=sorted(commune_nom_to_code.keys()).index(commune_default))
code_commune = commune_nom_to_code[commune_choisie]

sections = get_sections(code_commune)
parcelles = get_parcelles_geojson(code_commune)
section_codes = [s["properties"]["code"] for s in sections]
section_choisie = st.selectbox("Section cadastrale", section_codes)
code_section = section_choisie.zfill(5)
parcelles_section = [p for p in parcelles if p["id"][5:10] == code_section]
parcelle_ids = [p["id"] for p in parcelles_section]
parcelle_choisie = st.selectbox("📦 Parcelle", parcelle_ids)

parcelles_mutées = {parcelle_choisie}
m = generer_carte_complete(sections, parcelles_section, [], parcelles_mutées)
st_folium(m, width=700, height=500)

mutations = get_mutations_by_id_parcelle(parcelle_choisie)
df_mutations = normaliser_mutations(mutations) if mutations else pd.DataFrame()

st.subheader("Filtres DVF")
if df_mutations.empty:
    st.warning("❌ Aucune mutation DVF trouvée pour cette parcelle.")
else:
    types = sorted(df_mutations["Type local"].dropna().unique())
    type_filtre = st.multiselect("Type de bien", types, default=types)
    date_min_raw = pd.to_datetime(df_mutations["Date mutation"], dayfirst=True).min().date()
    date_max_raw = pd.to_datetime(df_mutations["Date mutation"], dayfirst=True).max().date()
    date_min = st.date_input("Date min", value=date_min_raw)
    date_max = st.date_input("Date max", value=date_max_raw)

    df_filtré = df_mutations[
        (df_mutations["Type local"].isin(type_filtre)) &
        (pd.to_datetime(df_mutations["Date mutation"], dayfirst=True) >= pd.Timestamp(date_min)) &
        (pd.to_datetime(df_mutations["Date mutation"], dayfirst=True) <= pd.Timestamp(date_max))
    ].copy()

    st.success(f"{len(df_filtré)} mutations filtrées")

    colonnes_droite = [col for col in [
        "Valeur foncière (€)", "Surface bâtie (m²)", "Lot Carrez (m²)",
        "Pièces", "Nombre de lots"
    ] if col in df_filtré.columns]

    colonnes_centre = [col for col in [
        "Date mutation", "Nature mutation", "Code postal"
    ] if col in df_filtré.columns]

    if not df_filtré.empty:
        styler = df_filtré.style \
            .set_properties(**{"text-align": "right"}, subset=colonnes_droite) \
            .set_properties(**{"text-align": "center"}, subset=colonnes_centre)
        st.dataframe(styler)
    else:
        st.info("Aucune mutation ne correspond aux filtres sélectionnés.")

# 📦 Export PDF
st.subheader("Export PDF de la tournée")
if st.button("Générer PDF"):
    generer_pdf(df)
    st.success("📄 PDF généré : fiche_tournee.pdf")
