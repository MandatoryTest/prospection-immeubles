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

def generer_carte_complete(sections, parcelles, mutation_points):
    # Centrage sur première parcelle ou section
    if parcelles:
        lat, lon = get_centroid(parcelles[0])
    elif sections:
        lat, lon = get_centroid(sections[0])
    else:
        lat, lon = 45.76, 4.85

    m = folium.Map(location=[lat, lon], zoom_start=17)

    # 🟦 Sections
    for s in sections:
        folium.GeoJson(
            s,
            name="Sections",
            style_function=lambda x: {"color": "blue", "weight": 1, "fillOpacity": 0.1},
            tooltip=s["properties"].get("code", "")
        ).add_to(m)

    # 🟩 Parcelles
    for p in parcelles:
        folium.GeoJson(
            p,
            name="Parcelles",
            style_function=lambda x: {"color": "green", "weight": 1, "fillOpacity": 0.2},
            tooltip=p["id"]
        ).add_to(m)

    # 🔴 Mutations
    for pt in mutation_points:
        lat = pt.get("latitude")
        lon = pt.get("longitude")
        popup = f"{pt.get('valeur_fonciere', 'N/A')} € - {pt.get('type_local', '')}"
        if lat and lon:
            folium.CircleMarker(
                location=[float(lat), float(lon)],
                radius=6,
                color="red",
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)

    folium.LayerControl().add_to(m)
    return m
