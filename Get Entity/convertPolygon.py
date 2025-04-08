import json
import os
import csv
import googlemaps
import folium
from shapely.geometry import shape, Point

# Konstanta
GEOJSON_PATH = "C:/Users/azrie/OneDrive/UNPAR/Materi Pembelajaran Informatika/Semester 6/Proyek Data Science 1/Tugas/Kode/Proyek-DS-1/GADM/kelurahan_bandung.geojson"
HTML_FOLDER = "html"
CSV_FOLDER = "csv"
SEARCH_RADIUS = 1000  # Radius pencarian dalam meter
API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ"

# Pastikan folder output ada
os.makedirs(HTML_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

# Buka file GeoJSON
gmaps = googlemaps.Client(key=API_KEY)
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

# Proses setiap kelurahan
for kelurahan_data in geojson_data["features"]:
    kelurahan_name = kelurahan_data["properties"].get("NAME_4", "Unknown")
    kelurahan_polygon = shape(kelurahan_data["geometry"])
    polygon_coords = kelurahan_data["geometry"]["coordinates"][0]
    centroid = kelurahan_polygon.centroid

    # Cari entitas di dalam kelurahan
    places_result = gmaps.places_nearby(
        location=(centroid.y, centroid.x),
        radius=SEARCH_RADIUS,
        type="hospital"
    )

    filtered_places = []
    for place in places_result.get("results", []):
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        point = Point(lng, lat)
        
        if kelurahan_polygon.contains(point):
            types = place.get("types", [])
            '''
            if "tempat_ibadah" in types:  # Pastikan ini adalah tempat ibadah bukan tempat dugem
                if "masjid" in types:
                    place_type = "Masjid"
                elif "gereja" in types:
                    place_type = "Gereja"
                elif "candi_hindu" in types:
                    place_type = "Kuil Hindu"
                elif "sinagoga" in types:
                    place_type = "Sinagoga"
                else:
                    place_type = "Tempat Ibadah Lainnya"
            '''
                    
            filtered_places.append({
                "name": place.get("name", "Unknown"),
                "address": place.get("vicinity", "Unknown"),
                "lat": lat,
                "lng": lng,
                #"type": place_type,
                "types": ", ".join(place.get("types", [])),
                "business_status": place.get("business_status", "Unknown"),
                "rating": place.get("rating", "Unknown"),
                "user_ratings_total": place.get("user_ratings_total", "Unknown"),
                # "price_level": place.get("price_level", "Unknown")
            })

    # Simpan hasil dalam file CSV
    csv_filename = os.path.join(CSV_FOLDER, f"{kelurahan_name}.csv")
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["name", "address", "lat", "lng", "types", "business_status", "rating", "user_ratings_total"])
        writer.writeheader()
        writer.writerows(filtered_places)
    
    
    if isinstance(polygon_coords[0][0], list):
        polygon_coords = polygon_coords[0]      

    # Buat peta
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15)
    folium.Polygon(
        locations=[(lat, lng) for lng, lat in polygon_coords],
        color="blue", fill=True, fill_color="lightblue", fill_opacity=0.5
    ).add_to(m)
    
    for place in filtered_places:
        '''
        if place["type"] == "Masjid":
            icon_color = "green"
        elif place["type"] == "Gereja":
            icon_color = "blue"
        elif place["type"] == "Kuil Hindu":
            icon_color = "orange"
        elif place["type"] == "Sinagoga":
            icon_color = "purple"
        else:
            icon_color = "red"
        '''
        folium.Marker(
            location=(place["lat"], place["lng"]),
            popup=place["name"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    # Simpan peta sebagai file HTML
    html_filename = os.path.join(HTML_FOLDER, f"{kelurahan_name}.html")
    m.save(html_filename)
    print(f"File {html_filename} dan {csv_filename} telah disimpan.")