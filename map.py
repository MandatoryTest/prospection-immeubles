import folium
from folium import GeoJson, GeoJsonTooltip

def generer_carte_complete(sections, parcelles, mutation_points, parcelles_mutées):
    # 📍 Centrage dynamique sur la première parcelle
    if parcelles:
        coords = parcelles[0]["geometry"]["coordinates"][0][0]
        lat, lon = coords[1], coords[0]
    else:
        lat, lon = 45.75, 4.85  # fallback Lyon

    m = folium.Map(
        location=[lat, lon],
        zoom_start=17,
        control_scale=False,
        zoom_control=True,      # ✅ autorisé
        dragging=False,         # ❌ désactivé
        scrollWheelZoom=False,  # ❌ désactivé
        doubleClickZoom=False,  # ❌ désactivé
        boxZoom=False,          # ❌ désactivé
        touchZoom=False         # ❌ désactivé
    )

    # 🗂️ Sections
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

    # 🧩 Parcelles
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
