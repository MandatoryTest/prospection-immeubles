import folium

def generer_carte_complete(sections, parcelles, mutation_points):
    m = folium.Map(location=[45.76, 4.85], zoom_start=16)

    for s in sections:
        folium.GeoJson(
            s,
            name="Section",
            style_function=lambda x: {"color": "blue", "fillOpacity": 0.1}
        ).add_to(m)

    for p in parcelles:
        folium.GeoJson(
            p,
            name="Parcelle",
            style_function=lambda x: {"color": "green", "fillOpacity": 0.2}
        ).add_to(m)

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
