<<<<<<< HEAD
import folium

def generer_carte(geojson, center=[45.76, 4.85], zoom=15):
    m = folium.Map(location=center, zoom_start=zoom)
    folium.GeoJson(geojson, name="Parcelles").add_to(m)
    return m

def generer_carte_parcelles(geojson, callback_url=None):
    m = folium.Map(location=[45.76, 4.85], zoom_start=15)
    for feature in geojson["features"]:
        parcelle_id = feature["id"]
        coords = feature["geometry"]["coordinates"][0][0]
        lon, lat = coords if isinstance(coords[0], float) else coords[0]
        popup = folium.Popup(f"Parcelle : {parcelle_id}", max_width=250)
        folium.Marker([lat, lon], popup=popup).add_to(m)
    return m
=======
import folium

def generer_carte(geojson, center=[45.76, 4.85], zoom=15):
    m = folium.Map(location=center, zoom_start=zoom)
    folium.GeoJson(geojson, name="Parcelles").add_to(m)
    return m
>>>>>>> 36d8982681a72f0a9e769e0284b39d72e49652b3
