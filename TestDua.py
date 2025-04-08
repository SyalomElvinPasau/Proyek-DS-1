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
GEOJSON_PATH = "C:/Users/HERMAN/Pictures/DEBBY/Semester 6/PDS1/PROYEK/Proyek-DS-1/GADM/kelurahan_bandung.geojson"
API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ"
OUTPUT_FOLDER = "output_kelurahan"
SEARCH_TYPE = "school"  # Bisa diganti

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
gmaps = googlemaps.Client(key=API_KEY)

# =============================
# Load Semua Kelurahan
# =============================
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

for idx, kelurahan_data in enumerate(geojson_data["features"]):
    kelurahan_name = kelurahan_data["properties"].get("NAME_4", f"Kelurahan_{idx}").replace("/", "-").replace(" ", "_")
    kelurahan_polygon = shape(kelurahan_data["geometry"])
    bounds = kelurahan_polygon.bounds

    print(f"\n=== Kelurahan: {kelurahan_name} ===")

    # =============================
    # Circle Packing - Hexagonal Grid
    # =============================
    polygon_width = bounds[2] - bounds[0]
    polygon_height = bounds[3] - bounds[1]
    CIRCLE_RADIUS = min(polygon_width, polygon_height) / 30
    HEX_WIDTH = 2 * CIRCLE_RADIUS
    HEX_HEIGHT = np.sqrt(3) * CIRCLE_RADIUS

    x_min, y_min, x_max, y_max = bounds
    x_vals = np.arange(x_min, x_max, HEX_WIDTH * 0.9)
    y_vals = np.arange(y_min, y_max, HEX_HEIGHT * 1.1)

    placed_circles = []
    circle_centers = []
    for i, x in enumerate(x_vals):
        for j, y in enumerate(y_vals):
            if i % 2 == 1:
                y += HEX_HEIGHT / 2
            center = Point(x, y)
            if kelurahan_polygon.contains(center):
                placed_circles.append((center, CIRCLE_RADIUS))
                circle_centers.append((center.y, center.x))

    # =============================
    # Google Places API Scraping
    # =============================
    results_all = []
    SEARCH_RADIUS = int(CIRCLE_RADIUS * 111000)

    for i, (lat, lng) in enumerate(circle_centers):
        print(f"  [{i+1}/{len(circle_centers)}] Scraping titik: ({lat}, {lng})")
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
            print(f"    ⚠️  Error di titik ({lat}, {lng}): {e}")
            continue

    # =============================
    # Simpan CSV per kelurahan
    # =============================
    if results_all:
        csv_path = os.path.join(OUTPUT_FOLDER, f"{kelurahan_name}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results_all[0].keys())
            writer.writeheader()
            writer.writerows(results_all)
        print(f"  ✅ Data disimpan: {csv_path} (Total: {len(results_all)})")
    else:
        print(f"  ⚠️  Tidak ada hasil scraping untuk {kelurahan_name}.")