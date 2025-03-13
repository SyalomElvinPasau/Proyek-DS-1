import json
from shapely.geometry import shape

# Buka file GeoJSON
with open("/home/elvin/Documents/Code/College/Proyek Data Science/Proyek-DS-1/GADM/kelurahan_bandung.geojson") as f:
    geojson_data = json.load(f)

# Ambil batas wilayah dari kelurahan tertentu
kelurahan_data = geojson_data["features"][0]  # Misal, ambil kelurahan pertama
kelurahan_name = kelurahan_data["properties"]["NAME_4"]
polygon_coords = kelurahan_data["geometry"]["coordinates"][0]  # Ambil koordinat polygon utama

# Buat Polygon dari koordinat
kelurahan_polygon = shape(kelurahan_data["geometry"])
# print(f"Kelurahan: {kelurahan_name}")




import googlemaps

API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ" 
gmaps = googlemaps.Client(key=API_KEY)

# Ambil titik pusat kelurahan (centroid)
centroid = kelurahan_polygon.centroid
search_radius = 1000  # Radius pencarian dalam meter

# Cari restoran di dalam kelurahan
places_result = gmaps.places_nearby(
    location=(centroid.y, centroid.x),  # (latitude, longitude)
    radius=search_radius,
    type="school"
)



from shapely.geometry import Point

filtered_places = []

for place in places_result.get("results", []):
    lat = place["geometry"]["location"]["lat"]
    lng = place["geometry"]["location"]["lng"]
    
    # Buat titik dari koordinat tempat
    point = Point(lng, lat)

    # Cek apakah titik ada dalam batas polygon kelurahan
    if kelurahan_polygon.contains(point):
        filtered_places.append({
            "name": place["name"],
            "address": place.get("vicinity", "Unknown"),
            "lat": lat,
            "lng": lng
        })

# Print hasil setelah difilter
print(json.dumps(filtered_places, indent=2))



import folium

# Buat peta dengan pusat di kelurahan
m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15)

# Tambahkan batas kelurahan ke peta
folium.Polygon(
    locations=[(lat, lng) for lng, lat in polygon_coords],
    color="blue",
    fill=True,
    fill_color="lightblue",
    fill_opacity=0.5
).add_to(m)

# Tambahkan lokasi tempat yang ditemukan
for place in filtered_places:
    folium.Marker(
        location=(place["lat"], place["lng"]),
        popup=place["name"],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# Simpan dan buka peta
map_file = "map_kelurahan.html"
m.save(map_file)
print(f"Peta telah disimpan sebagai {map_file}")


