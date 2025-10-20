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

def generer_carte_complete(sections, parcelles, mutation_points, parcelles_mutées=None):
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

    # 🟩 / 🟥 Parcelles cliquables sans popup
    parcelles_mutées = parcelles_mutées or set()
    for p in parcelles:
        pid = p["id"]
        color = "red" if pid in parcelles_mutées else "green"
        folium.GeoJson(
            p,
            name="Parcelles",
            style_function=lambda x, c=color: {"color": c, "weight": 1, "fillOpacity": 0.2},
            tooltip=pid,
            highlight_function=lambda x: {"weight": 3, "color": "orange"}
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

def format_valeur(valeur):
    try:
        montant = float(valeur)
        return f"{montant:,.2f}".replace(",", " ").replace(".", ",") + " €"
    except:
        return "N/A"
