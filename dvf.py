import requests

BASE_URL = "https://app.dvf.etalab.gouv.fr"

# 🔍 Mutations DVF par section cadastrale
def get_mutations(code_commune: str, section: str):
    section = section.zfill(5)  # Assure 5 caractères
    url = f"{BASE_URL}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("mutations", [])
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# 📍 Parcelles extraites depuis les mutations DVF
def get_parcelles_from_mutations(code_commune: str, section: str):
    section = section.zfill(5)
    mutations = get_mutations(code_commune, section)
    if isinstance(mutations, list):
        parcelles = set()
        for m in mutations:
            for p in m.get("parcelles", []):
                parcelles.add(p.get("id_parcelle"))
        return sorted(parcelles)
    else:
        return []

# 🔎 Mutations DVF par parcelle spécifique
def get_mutations_by_parcelle(parcelle_id: str):
    url = f"{BASE_URL}/api/parcelles2/{parcelle_id}/from=2020-01-01&to=2025-12-31"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("mutations", [])
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# 🏙️ Liste des communes + arrondissements du département
def get_communes_du_departement(code_departement="69"):
    try:
        # Communes classiques
        r1 = requests.get(f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code")
        communes = r1.json() if r1.status_code == 200 else []

        # Arrondissements municipaux
        r2 = requests.get("https://app.dvf.etalab.gouv.fr/donneesgeo/arrondissements_municipaux-20180711.json")
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

# 🔁 Mapping INSEE → cadastre (pour sections et parcelles)
def get_commune_cadastre_codes(code_commune):
    url = "https://app.dvf.etalab.gouv.fr/donneesgeo/communes-mapping.json"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            mapping = r.json()
            return mapping.get(code_commune, [code_commune])
        else:
            return [code_commune]
    except Exception:
        return [code_commune]

# 📦 Sections cadastrales (via cadastre.data.gouv.fr)
def get_sections_geojson(code_commune):
    codes = get_commune_cadastre_codes(code_commune)
    features = []
    for c in codes:
        url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{c}/geojson/sections"
        try:
            r = requests.get(url)
            if r.status_code == 200 and "features" in r.json():
                features += r.json()["features"]
        except Exception:
            continue
    return features
