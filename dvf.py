import requests

BASE_URL = "https://app.dvf.etalab.gouv.fr"

def get_mutations(code_commune: str, section: str):
    url = f"{BASE_URL}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()["mutations"]
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_mutations_by_parcelle(parcelle_id: str):
    url = f"{BASE_URL}/api/parcelles2/{parcelle_id}/from=2020-01-01&to=2025-12-31"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()["mutations"]
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_communes_du_departement(code_departement="69"):
    url = f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except Exception:
        return []

def get_sections_geojson(code_commune):
    url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_commune}/geojson/sections"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()["features"]
        else:
            return []
    except Exception:
        return []

def get_parcelles_geojson(code_commune):
    url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_commune}/geojson/parcelles"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()["features"]
        else:
            return []
    except Exception:
        return []
