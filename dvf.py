import requests
import pandas as pd

BASE_DVF = "https://app.dvf.etalab.gouv.fr"
BASE_CADASTRE = "https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes"

def get_communes_du_departement(code_departement="69"):
    try:
        url = f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code"
        print(f"📡 get_communes_du_departement → {url}")
        r1 = requests.get(url, timeout=5)
        communes = r1.json() if r1.status_code == 200 else []

        url_arr = f"{BASE_DVF}/donneesgeo/arrondissements_municipaux-20180711.json"
        r2 = requests.get(url_arr, timeout=5)
        arrondissements = r2.json()["features"] if r2.status_code == 200 else []

        for a in arrondissements:
            props = a["properties"]
            if props["code"].startswith(code_departement):
                communes.append({
                    "nom": props["nom"],
                    "code": props["code"]
                })

        return sorted(communes, key=lambda c: c["nom"])
    except Exception as e:
        print(f"❌ Erreur get_communes_du_departement: {e}")
        return []

def get_sections(code_commune):
    url = f"{BASE_CADASTRE}/{code_commune}/geojson/sections"
    print(f"📡 get_sections → {url}")
    try:
        r = requests.get(url, timeout=5)
        print(f"📬 Statut : {r.status_code}")
        data = r.json() if r.status_code == 200 else {}
        features = data.get("features", [])
        print(f"✅ Sections récupérées : {len(features)}")
        return features if isinstance(features, list) else []
    except Exception as e:
        print(f"❌ Erreur get_sections: {e}")
        return []

def get_parcelles_geojson(code_commune):
    url = f"{BASE_CADASTRE}/{code_commune}/geojson/parcelles"
    print(f"📡 get_parcelles_geojson → {url}")
    try:
        r = requests.get(url, timeout=5)
        data = r.json() if r.status_code == 200 else {}
        features = data.get("features", [])
        print(f"✅ Parcelles récupérées : {len(features)}")
        return features if isinstance(features, list) else []
    except Exception as e:
        print(f"❌ Erreur get_parcelles_geojson: {e}")
        return []

def get_mutations_by_id_parcelle(id_parcelle):
    url = f"{BASE_DVF}/api/parcelles2/{id_parcelle}/from=2020-01-01&to=2025-12-31"
    print(f"📡 get_mutations_by_id_parcelle → {url}")
    try:
        r = requests.get(url, timeout=5)
        mutations = r.json().get("mutations", []) if r.status_code == 200 else []
        print(f"✅ Mutations récupérées : {len(mutations)}")
        return mutations
    except Exception as e:
        print(f"❌ Erreur get_mutations_by_id_parcelle: {e}")
        return []

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def normaliser_mutations(mutations):
    lignes = []
    for mutation in mutations:
        infos = mutation.get("infos", [])
        for info in infos:
            valeur = safe_float(info.get("valeur_fonciere"))
            surface = safe_float(info.get("surface_reelle_bati"))
            carrez = safe_float(info.get("lot1_surface_carrez"))
            pieces = safe_int(info.get("nombre_pieces_principales"))
            lots = safe_int(info.get("nombre_lots"))
            date = pd.to_datetime(info.get("date_mutation"), errors="coerce").strftime("%d/%m/%Y")

            adresse = f"{info.get('adresse_numero', '')} {info.get('adresse_nom_voie', '')}".strip()
            adresse = " ".join(adresse.split())

            lignes.append({
                "Date mutation": date,
                "Nature mutation": info.get("nature_mutation"),
                "Valeur foncière (€)": f"{valeur:,.0f}".replace(",", " ").replace(".", ",") + " €",
                "Type local": info.get("type_local"),
                "Surface bâtie (m²)": f"{surface:.2f}",
                "Lot Carrez (m²)": f"{carrez:.2f}",
                "Pièces": pieces,
                "Nombre de lots": lots,
                "Adresse": adresse,
                "Code postal": info.get("code_postal"),
                "Commune": info.get("nom_commune"),
                "Section": info.get("section_prefixe"),
                "Parcelle": info.get("id_parcelle")
            })
    df = pd.DataFrame(lignes)
    colonnes = [
        "Date mutation", "Nature mutation", "Valeur foncière (€)",
        "Type local", "Surface bâtie (m²)", "Lot Carrez (m²)", "Pièces",
        "Nombre de lots", "Adresse", "Code postal", "Commune",
        "Section", "Parcelle"
    ]
    df = df[colonnes]
    df = df.sort_values("Date mutation", ascending=False)
    print(f"📊 normaliser_mutations → {df.shape[0]} lignes")
    return df
