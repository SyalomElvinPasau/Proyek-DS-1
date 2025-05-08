import json
import os
import csv
import numpy as np
import googlemaps
import matplotlib.pyplot as plt
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from matplotlib.patches import Polygon as MplPolygon, Circle as MplCircle

# =============================
# Konfigurasi
# =============================
GEOJSON_PATH = "C:/Users/azrie/OneDrive/UNPAR/Materi Pembelajaran Informatika/Semester 6/Proyek Data Science 1/Tugas/Kode/Proyek-DS-1/GADM/kelurahan_bandung.geojson"  # Ganti jika path beda
API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ"
OUTPUT_FOLDER = "output"
CSV_FILENAME = "circle_packing_scrape.csv"
SEARCH_TYPE = "school"  # Bisa diganti: restaurant, hospital, dst

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
gmaps = googlemaps.Client(key=API_KEY)

# =============================
# Load polygon kelurahan
# =============================
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

kelurahan_data = geojson_data["features"][60]  # !! GANTI KELURAHAN DI SINI
kelurahan_polygon = shape(kelurahan_data["geometry"])
bounds = kelurahan_polygon.bounds

# =============================
# Circle Packing - Hexagonal Grid
# =============================
# Define Hexagonal Grid Parameters
polygon_width = bounds[2] - bounds[0]
polygon_height = bounds[3] - bounds[1]
CIRCLE_RADIUS = min(polygon_width, polygon_height) / 30 # !!NGatur ukuran lingkaran
HEX_WIDTH = 2 * CIRCLE_RADIUS # Horizontal spacing
HEX_HEIGHT = np.sqrt(3) * CIRCLE_RADIUS # Vertical spacing

# Generate hexagonal grid of points
x_min, y_min, x_max, y_max = bounds
x_vals = np.arange(x_min, x_max, HEX_WIDTH * 0.9) # !!Ngatur lebar lingkaran buat adjustment barangkali overapping
y_vals = np.arange(y_min, y_max, HEX_HEIGHT * 1.1) # !!Ngatur tinggi lingkaran, fungsinya sama

# Store placed circles
placed_circles = []
circle_shapes = []
circle_centers = []

for i, x in enumerate(x_vals):
    for j, y in enumerate(y_vals): # Ensure circle is inside polygon
        if i % 2 == 1: # Stagger odd rows
            y += HEX_HEIGHT / 2
        center = Point(x, y)
        if kelurahan_polygon.contains(center):
            placed_circles.append((center, CIRCLE_RADIUS))
            circle_shapes.append(center.buffer(CIRCLE_RADIUS))
            circle_centers.append((center.y, center.x))  # lat, lng

# =============================
# Google Places API Scraping
# =============================
results_all = []
SEARCH_RADIUS = int(CIRCLE_RADIUS * 111000)  # approx derajat ke meter

for i, (lat, lng) in enumerate(circle_centers):
    print(f"[{i+1}/{len(circle_centers)}] Scraping titik: ({lat}, {lng}) ...")
    try:
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=SEARCH_RADIUS,
            type=SEARCH_TYPE
        )

        for place in places_result.get("results", []):
            results_all.append({
                "center_lat": lat,
                "center_lng": lng,
                "name": place.get("name", "Unknown"),
                "address": place.get("vicinity", "Unknown"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "business_status": place.get("business_status", "Unknown"),
                "rating": place.get("rating", "Unknown"),
                "user_ratings_total": place.get("user_ratings_total", "Unknown"),
                "types": ", ".join(place.get("types", []))
            })
    except Exception as e:
        print(f"  ⚠️  Error di titik ({lat}, {lng}): {e}")
        continue

# =============================
# Simpan ke CSV
# =============================
csv_path = os.path.join(OUTPUT_FOLDER, CSV_FILENAME)
if results_all:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results_all[0].keys())
        writer.writeheader()
        writer.writerows(results_all)
    print(f"\n✅ Scraping selesai! Total data: {len(results_all)}")
    print(f"📄 Data disimpan di: {csv_path}")
else:
    print("❌ Tidak ada data hasil scraping.")

# =============================
# Visualisasi
# =============================
fig, ax = plt.subplots(figsize=(8, 8))
polygon_coords = np.array(kelurahan_polygon.exterior.coords)
polygon_patch = MplPolygon(polygon_coords, closed=True, edgecolor='blue', facecolor='lightblue', alpha=0.5)
ax.add_patch(polygon_patch)

for center, radius in placed_circles:
    circle_patch = MplCircle((center.x, center.y), radius, color='red', alpha=0.5)
    ax.add_patch(circle_patch)

ax.set_xlim(bounds[0] - CIRCLE_RADIUS, bounds[2] + CIRCLE_RADIUS)
ax.set_ylim(bounds[1] - CIRCLE_RADIUS, bounds[3] + CIRCLE_RADIUS)
ax.set_aspect('equal')
plt.title(f"Circle Packing & Scraping: {SEARCH_TYPE.title()}\nTotal Titik: {len(circle_centers)}")
plt.grid(True)
plt.show()