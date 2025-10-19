import streamlit as st
import requests
import pandas as pd

@st.cache_data
def get_communes_du_departement(code_departement):
    url = f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code"
    return requests.get(url).json()

@st.cache_data
def get_sections(code_commune):
    url = f"https://cadastre.data.gouv.fr/api/communes/{code_commune}/sections"
    return requests.get(url).json()["features"]

@st.cache_data
def get_parcelles_geojson(code_commune):
    url = f"https://cadastre.data.gouv.fr/api/communes/{code_commune}/parcelles"
    return requests.get(url).json()["features"]

def get_mutations_by_id_parcelle(id_parcelle):
    url = f"https://app.dvf.etalab.gouv.fr/api/mutations/{id_parcelle}"
    return requests.get(url).json()

def normaliser_mutations(mutations):
    lignes = []
    for mutation in mutations:
        for info in mutation.get("infos", []):
            valeur = float(info.get("valeur_fonciere", 0))
            valeur_formatée = f"{valeur:,.2f}".replace(",", " ").replace(".", ",") + " €"
            lignes.append({
                "Date mutation": pd.to_datetime(mutation.get("date_mutation")),
                "Valeur foncière (€)": valeur_formatée,
                "Type local": info.get("type_local", ""),
                "Surface": info.get("surface_reelle_bati", ""),
                "Adresse": info.get("adresse", ""),
                "id_parcelle": info.get("id_parcelle", "")
            })
    return pd.DataFrame(lignes)
