import requests

BASE_DVF = "https://app.dvf.etalab.gouv.fr"

def get_communes_du_departement(code_departement="69"):
    try:
        # Communes classiques
        r1 = requests.get(f"https://geo.api.gouv.fr/departements/{code_departement}/communes?fields=nom,code")
        communes = r1.json() if r1.status_code == 200 else []

        # Arrondissements municipaux
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
    url = f"{BASE_DVF}/api/sections/{code_commune}"
    try:
        r = requests.get(url)
        return r.json().get("sections", []) if r.status_code == 200 else []
    except Exception:
        return []

def get_mutations(code_commune, section):
    if not section:
        return {"error": "Section cadastrale manquante"}
    section = str(section).zfill(5)
    url = f"{BASE_DVF}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        return r.json().get("mutations", []) if r.status_code == 200 else []
    except Exception:
        return []

def get_parcelles_from_mutations(code_commune, section):
    mutations = get_mutations(code_commune, section)
    if isinstance(mutations, list):
        parcelles = set()
        for m in mutations:
            for p in m.get("parcelles", []):
                parcelles.add(p.get("id_parcelle"))
        return sorted(parcelles)
    else:
        return []

def get_mutations_by_parcelle(code_commune, section, parcelle_id):
    mutations = get_mutations(code_commune, section)
    if isinstance(mutations, list):
        return [
            m for m in mutations
            if parcelle_id in [p["id_parcelle"] for p in m.get("parcelles", [])]
        ]
    else:
        return []
