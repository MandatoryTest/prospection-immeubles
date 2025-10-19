import requests

BASE_URL = "https://app.dvf.etalab.gouv.fr"

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

def get_parcelles_from_mutations(code_commune: str, section: str):
    section = section.zfill(5)
    url = f"{BASE_URL}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            mutations = r.json().get("mutations", [])
            parcelles = set()
            for m in mutations:
                for p in m.get("parcelles", []):
                    parcelles.add(p.get("id_parcelle"))
            return sorted(parcelles)
        else:
            return []
    except Exception:
        return []
