import json
import os
import numpy as np
import googlemaps
import folium
import csv
from shapely.geometry import shape, Point
from shapely.ops import transform
from collections import deque
from pyproj import Transformer

# ==============================
# Konfigurasi
# ==============================
GEOJSON_PATH = "C:/Users/i22077/Proyek-DS-1/GADM/kelurahan_bandung.geojson"  # Ganti dengan path ke file GeoJSON kelurahan Bandung
API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ"  # Ganti dengan API key Google Anda
OUTPUT_FOLDER = "output_2"
CSV_FILENAME = "scraped_places.csv"
SEARCH_TYPE = "hospital"  # Bisa diganti: restaurant, school, dll.
STEP_SIZE_M = 50  # Jarak antar titik sampling dalam meter

# ==============================
# Inisialisasi
# ==============================
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
gmaps = googlemaps.Client(key=API_KEY)

# ==============================
# Load polygon kelurahan
# ==============================
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

kelurahan_name = 'Cibuntu'
kelurahan_data = None

for kelurahan in geojson_data["features"]:
    if kelurahan["properties"].get("NAME_4") == kelurahan_name:
        kelurahan_data = kelurahan
        break

if kelurahan_data is None:
    print(f"Kelurahan {kelurahan_name} tidak ditemukan.")
    exit()

kelurahan_polygon = shape(kelurahan_data["geometry"])

# ==============================
# Tambah Buffer 1km dari Polygon Kelurahan
# ==============================
# Gunakan proyeksi UTM zona 48S untuk Bandung
project_to_utm = Transformer.from_crs("epsg:4326", "epsg:32748", always_xy=True).transform
project_to_wgs = Transformer.from_crs("epsg:32748", "epsg:4326", always_xy=True).transform

kelurahan_utm = transform(project_to_utm, kelurahan_polygon)
buffered_utm = kelurahan_utm.buffer(1000)  # buffer 1000 meter
buffered_polygon = transform(project_to_wgs, buffered_utm)

# ==============================
# Flood Fill untuk Titik Sampling
# ==============================
STEP_DEG = STEP_SIZE_M / 111000  # approx meter ke derajat
start_point = kelurahan_polygon.centroid
visited = set()
queue = deque()
circle_centers = []

queue.append((start_point.x, start_point.y))  # lng, lat

while queue:
    x, y = queue.popleft()
    point = Point(x, y)

    if (x, y) in visited:
        continue
    visited.add((x, y))

    if not kelurahan_polygon.contains(point):
        continue

    circle_centers.append((y, x))  # lat, lng

    neighbors = [
        (x + STEP_DEG, y),
        (x - STEP_DEG, y),
        (x, y + STEP_DEG),
        (x, y - STEP_DEG),
    ]

    for nx, ny in neighbors:
        if (nx, ny) not in visited:
            queue.append((nx, ny))

# ==============================
# Google Places API Scraping
# ==============================
results_all = []
SEARCH_RADIUS = STEP_SIZE_M

for i, (lat, lng) in enumerate(circle_centers):
    try:
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=SEARCH_RADIUS,
            type=SEARCH_TYPE
        )

        for place in places_result.get("results", []):
            place_lat = place["geometry"]["location"]["lat"]
            place_lng = place["geometry"]["location"]["lng"]
            place_point = Point(place_lng, place_lat)

            # Gunakan buffered_polygon.contains jika ingin data dari buffer 1km
            if buffered_polygon.contains(place_point):  # Ganti ini jika hanya ingin yang di dalam kelurahan
                results_all.append({
                    "name": place.get("name", "Unknown"),
                    "address": place.get("vicinity", "Unknown"),
                    "lat": place_lat,
                    "lng": place_lng
                })
    except Exception as e:
        print(f"  ⚠️  Error at point ({lat}, {lng}): {e}")
        continue

# ==============================
# Simpan Data ke CSV
# ==============================
csv_path = os.path.join(OUTPUT_FOLDER, CSV_FILENAME)
if results_all:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results_all[0].keys())
        writer.writeheader()
        writer.writerows(results_all)
    print(f"\n✅ Scraping dan penyimpanan CSV selesai! Hasil disimpan di: {csv_path}")
else:
    print("❌ Tidak ada data ditemukan dalam polygon kelurahan yang ditentukan.")

# ==============================
# Visualisasi dengan Folium
# ==============================
centroid = kelurahan_polygon.centroid
m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15)

# Tambahkan polygon kelurahan (biru muda)
if kelurahan_polygon.geom_type == 'MultiPolygon':
    for polygon in kelurahan_polygon.geoms:
        coords = np.array(polygon.exterior.coords)
        folium.Polygon(
            locations=[(lat, lng) for lng, lat in coords],
            color="blue", fill=True, fill_color="lightblue", fill_opacity=0.5
        ).add_to(m)
else:
    coords = np.array(kelurahan_polygon.exterior.coords)
    folium.Polygon(
        locations=[(lat, lng) for lng, lat in coords],
        color="blue", fill=True, fill_color="lightblue", fill_opacity=0.5
    ).add_to(m)

# Tambahkan buffer 1km (ungu)
if buffered_polygon.geom_type == 'MultiPolygon':
    for poly in buffered_polygon.geoms:
        coords = np.array(poly.exterior.coords)
        folium.Polygon(
            locations=[(lat, lng) for lng, lat in coords],
            color="purple", weight=2, fill=False
        ).add_to(m)
else:
    coords = np.array(buffered_polygon.exterior.coords)
    folium.Polygon(
        locations=[(lat, lng) for lng, lat in coords],
        color="purple", weight=2, fill=False
    ).add_to(m)

# Tambahkan titik sampling
for lat, lng in circle_centers:
    folium.CircleMarker(
        location=[lat, lng],
        radius=2,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.5
    ).add_to(m)

# Tambahkan marker untuk tempat yang ditemukan
for result in results_all:
    folium.Marker(
        location=(result["lat"], result["lng"]),
        popup=f"{result['name']} - {result['address']}",
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)

# Simpan peta sebagai file HTML
html_filename = os.path.join(OUTPUT_FOLDER, f"{kelurahan_name}_map.html")
m.save(html_filename)
print(f"\n✅ Peta disimpan di: {html_filename}")
