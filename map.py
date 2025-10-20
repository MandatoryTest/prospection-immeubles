import folium
from folium import GeoJson, GeoJsonTooltip

def generer_carte_complete(sections, parcelles, mutation_points, parcelles_mutées):
    # 📍 Carte centrée sur Lyon (modifiable dynamiquement si besoin)
    m = folium.Map(
        location=[45.75, 4.85],
        zoom_start=15,
        control_scale=False,
        zoom_control=False,
        dragging=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        boxZoom=False,
        touchZoom=False
    )

    # 🗂️ Ajout des sections
    for section in sections:
        GeoJson(
            section,
            style_function=lambda x: {
                "fillColor": "#cccccc",
                "color": "#999999",
                "weight": 1,
                "fillOpacity": 0.2
            }
        ).add_to(m)

    # 🧩 Ajout des parcelles
    for parcelle in parcelles:
        id_parcelle = parcelle["id"]
        surbrillance = id_parcelle in parcelles_mutées
        GeoJson(
            parcelle,
            style_function=lambda x, surbrillance=surbrillance: {
                "fillColor": "#ffcc00" if surbrillance else "#ffffff",
                "color": "#ff9900" if surbrillance else "#cccccc",
                "weight": 2 if surbrillance else 1,
                "fillOpacity": 0.6 if surbrillance else 0.1
            },
            tooltip=GeoJsonTooltip(fields=["id"], aliases=["Parcelle"])
        ).add_to(m)

    return m
