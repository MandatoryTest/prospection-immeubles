from streamlit import cache_data
from dvf import (
    get_communes_du_departement,
    get_sections,
    get_parcelles_geojson,
    get_mutations_by_id_parcelle
)

@cache_data
def get_communes(departement):
    return get_communes_du_departement(departement)

@cache_data
def get_sections(code_commune):
    return get_sections(code_commune)

@cache_data
def get_parcelles(code_commune):
    return get_parcelles_geojson(code_commune)

@cache_data
def get_mutations(id_parcelle):
    return get_mutations_by_id_parcelle(id_parcelle)
