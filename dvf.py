import requests
import pandas as pd

BASE_DVF = "https://app.dvf.etalab.gouv.fr"
BASE_CADASTRE = "https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes"

def get_communes_du_departement(code_departement="69"):
    try:
        r1 = requests.get(f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code")
        communes = r1.json() if r1.status_code == 200 else []

        r2 = requests.get(f"{BASE_DVF}/donneesgeo/arrondissements_municipaux-20180711.json")
        arrondissements = r2.json()["features"] if r2.status_code == 200 else []

        for a in arrondissements:
            props = a["properties"]
            if props["code"].startswith(code_departement):
                communes.append({
                    "nom": props["nom"],
                    "code": props["code"]
                })

        return sorted(communes, key=lambda c: c["nom"])
    except Exception:
        return []

def get_sections(code_commune):
    url = f"{BASE_CADASTRE}/{code_commune}/geojson/sections"
    try:
        r = requests.get(url)
        if r.status_code == 200 and "features" in r.json():
            features = r.json()["features"]
            return sorted({f["properties"]["code"] for f in features})
        else:
            return []
    except Exception:
        return []

def get_parcelles_geojson(code_commune):
    url = f"{BASE_CADASTRE}/{code_commune}/geojson/parcelles"
    try:
        r = requests.get(url)
        if r.status_code == 200 and "features" in r.json():
            return r.json()["features"]
        else:
            return []
    except Exception:
        return []

def get_mutations_by_id_parcelle(id_parcelle):
    url = f"{BASE_DVF}/api/parcelles2/{id_parcelle}/from=2020-01-01&to=2025-12-31"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("mutations", [])
        else:
            return []
    except Exception:
        return []

def normaliser_mutations(mutations):
    lignes = []
    for m in mutations:
        lignes.append({
            "Date": m.get("date_mutation"),
            "Valeur foncière (€)": m.get("valeur_fonciere"),
            "Type local": m.get("type_local"),
            "Surface (m²)": m.get("surface_reelle_bati"),
            "Adresse": m.get("adresse"),
            "Code commune": m.get("code_commune"),
            "Section": m.get("parcelles", [{}])[0].get("section"),
            "Parcelle": m.get("parcelles", [{}])[0].get("id_parcelle")
        })
    return pd.DataFrame(lignes)
