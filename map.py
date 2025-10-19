import folium

def get_centroid(feature):
    coords = feature["geometry"]["coordinates"]
    if feature["geometry"]["type"] == "Polygon":
        lon, lat = coords[0][0]
    elif feature["geometry"]["type"] == "MultiPolygon":
        lon, lat = coords[0][0][0]
    else:
        lon, lat = 4.85, 45.76
    return lat, lon

def generer_carte_interactive(sections, parcelles):
    lat, lon = get_centroid(sections[0]) if sections else (45.76, 4.85)
    m = folium.Map(location=[lat, lon], zoom_start=16)

    # 🟦 Sections
    for s in sections:
        s["properties"]["id"] = s["properties"]["code"]
        s["properties"]["type"] = "section"
        folium.GeoJson(
            s,
            name="Sections",
            style_function=lambda x: {"color": "blue", "weight": 1, "fillOpacity": 0.1},
            highlight_function=lambda x: {"weight": 3, "color": "orange"},
            tooltip=s["properties"]["code"]
        ).add_to(m)

    # 🟩 Parcelles
    for p in parcelles:
        p["properties"]["id"] = p["id"]
        p["properties"]["type"] = "parcelle"
        folium.GeoJson(
            p,
            name="Parcelles",
            style_function=lambda x: {"color": "green", "weight": 1, "fillOpacity": 0.2},
            highlight_function=lambda x: {"weight": 3, "color": "orange"},
            tooltip=p["id"]
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m
