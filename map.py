import folium

def generer_carte_mutations(mutations):
    m = folium.Map(location=[45.76, 4.85], zoom_start=15)
    for mtn in mutations:
        lat = mtn.get("latitude")
        lon = mtn.get("longitude")
        if lat and lon:
            popup = folium.Popup(f"{mtn.get('date_mutation')} – {mtn.get('valeur_fonciere')} €", max_width=250)
            folium.Marker([lat, lon], popup=popup).add_to(m)
    return m
