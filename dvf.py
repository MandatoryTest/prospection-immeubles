import requests

BASE_URL = "https://app.dvf.etalab.gouv.fr"

def get_communes_du_departement(code_departement="69"):
    url = f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code"
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def get_sections(code_commune):
    url = f"{BASE_URL}/api/sections/{code_commune}"
    try:
        r = requests.get(url)
        return r.json().get("sections", []) if r.status_code == 200 else []
    except Exception:
        return []

def get_mutations(code_commune, section):
    section = section.zfill(5)
    url = f"{BASE_URL}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        return r.json().get("mutations", []) if r.status_code == 200 else []
    except Exception:
        return []

def get_parcelles_from_mutations(code_commune, section):
    mutations = get_mutations(code_commune, section)
    parcelles = set()
    for m in mutations:
        for p in m.get("parcelles", []):
            parcelles.add(p.get("id_parcelle"))
    return sorted(parcelles)

def get_mutations_by_parcelle(code_commune, section, parcelle_id):
    mutations = get_mutations(code_commune, section)
    return [
        m for m in mutations
        if parcelle_id in [p["id_parcelle"] for p in m.get("parcelles", [])]
    ]
