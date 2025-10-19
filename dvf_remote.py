import requests

BASE_URL = "https://app.dvf.etalab.gouv.fr"

def get_mutations(code_commune: str, section: str):
    """Récupère les mutations DVF d'une section cadastrale via l'API publique"""
    url = f"{BASE_URL}/api/mutations3/{code_commune}/{section}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()["mutations"]
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_parcelles_geojson(code_commune: str):
    """Récupère les parcelles cadastrales via cadastre.data.gouv.fr"""
    url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_commune}/geojson/parcelles"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"Code {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}
