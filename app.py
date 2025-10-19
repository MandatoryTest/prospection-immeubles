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
