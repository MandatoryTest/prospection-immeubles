import folium

def generer_carte_parcelles(geojson_features):
    m = folium.Map(location=[45.76, 4.85], zoom_start=17)
    for feature in geojson_features:
        coords = feature["geometry"]["coordinates"]
        if feature["geometry"]["type"] == "Polygon":
            lon, lat = coords[0][0]
        elif feature["geometry"]["type"] == "MultiPolygon":
            lon, lat = coords[0][0][0]
        else:
            continue
        popup = folium.Popup(feature["id"], max_width=250)
        folium.Marker([lat, lon], popup=popup).add_to(m)
    return m
