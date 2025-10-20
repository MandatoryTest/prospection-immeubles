import folium
from folium import GeoJson

def generer_carte_complete(sections, parcelles, mutations, surbrillance):
    m = folium.Map(location=[45.76, 4.85], zoom_start=14)

    def style_parcelle(feature):
        id_parcelle = feature["id"]
        return {
            "color": "red" if id_parcelle in surbrillance else "gray",
            "weight": 3 if id_parcelle in surbrillance else 1,
            "fillOpacity": 0.2
        }

    for f in parcelles:
        gj = GeoJson(
            f,
            style_function=style_parcelle,
            tooltip=folium.Tooltip(f["id"])
        )
        gj.add_to(m)

    return m
