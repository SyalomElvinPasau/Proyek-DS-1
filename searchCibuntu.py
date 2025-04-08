import json
import os
import numpy as np
import googlemaps
import folium
import csv
from shapely.geometry import shape, Point
from shapely.ops import unary_union

# ==============================
# Konfigurasi
# ==============================
GEOJSON_PATH = "/home/elvin/Documents/Code/College/Proyek Data Science/Proyek-DS-1/GADM/kelurahan_bandung.geojson"  # Ganti jika path beda
API_KEY = "AIzaSyAHKvXsFJWeXNiydLFuaJRrNKbd-3KUoOQ"  # Replace with your actual API key
OUTPUT_FOLDER = "output"
CSV_FILENAME = "scraped_places.csv"
SEARCH_TYPE = "hospital"  # Can be changed to: restaurant, hospital, etc.

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
gmaps = googlemaps.Client(key=API_KEY)

# ==============================
# Load polygon kelurahan
# ==============================
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

# Filter kelurahan 'Ciumbuleuit'
kelurahan_name = 'Ciumbuleuit'
kelurahan_data = None

for kelurahan in geojson_data["features"]:
    if kelurahan["properties"].get("NAME_4") == kelurahan_name:
        kelurahan_data = kelurahan
        break

if kelurahan_data is None:
    print(f"Kelurahan {kelurahan_name} tidak ditemukan.")
else:
    kelurahan_polygon = shape(kelurahan_data["geometry"])
    bounds = kelurahan_polygon.bounds

    # ==============================
    # Circle Packing - Hexagonal Grid
    # ==============================
    polygon_width = bounds[2] - bounds[0]
    polygon_height = bounds[3] - bounds[1]
    CIRCLE_RADIUS = min(polygon_width, polygon_height) / 30  # Set circle size
    HEX_WIDTH = 2 * CIRCLE_RADIUS  # Horizontal spacing
    HEX_HEIGHT = np.sqrt(3) * CIRCLE_RADIUS  # Vertical spacing

    # Generate hexagonal grid of points
    x_min, y_min, x_max, y_max = bounds
    x_vals = np.arange(x_min, x_max, HEX_WIDTH * 0.9)  # Adjust width for better fitting
    y_vals = np.arange(y_min, y_max, HEX_HEIGHT * 1.1)  # Adjust height for better fitting

    # Store placed circles
    placed_circles = []
    circle_shapes = []
    circle_centers = []

    for i, x in enumerate(x_vals):
        for j, y in enumerate(y_vals):
            if i % 2 == 1:  # Stagger odd rows
                y += HEX_HEIGHT / 2
            center = Point(x, y)
            if kelurahan_polygon.contains(center):
                placed_circles.append((center, CIRCLE_RADIUS))
                circle_shapes.append(center.buffer(CIRCLE_RADIUS))
                circle_centers.append((center.y, center.x))  # lat, lng

    # ==============================
    # Google Places API Scraping
    # ==============================
    results_all = []
    SEARCH_RADIUS = int(CIRCLE_RADIUS * 111000)  # approx degree to meters

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

                # Only include the place if it's inside the kelurahan polygon
                if kelurahan_polygon.contains(place_point):
                    results_all.append({
                        # v"center_lat": lat,
                        # "center_lng": lng,
                        "name": place.get("name", "Unknown"),
                        "address": place.get("vicinity", "Unknown"),
                        "lat": place_lat,
                        "lng": place_lng,
                        "rating": place.get("rating", "Unknown"),
                        "user_ratings_total": place.get("user_ratings_total", "Unknown")
                    })
        except Exception as e:
            print(f"  ⚠️  Error at point ({lat}, {lng}): {e}")
            continue

    # ==============================
    # Save Scraped Data to CSV
    # ==============================
    csv_path = os.path.join(OUTPUT_FOLDER, CSV_FILENAME)
    if results_all:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results_all[0].keys())
            writer.writeheader()
            writer.writerows(results_all)
        print(f"\n✅ Scraping and CSV generation completed! Results saved in: {csv_path}")
    else:
        print("❌ No data found in the specified kelurahan polygon.")

    # ==============================
    # Visualize using Folium (instead of matplotlib)
    # ==============================
    # Create a map centered at the centroid of the kelurahan
    centroid = kelurahan_polygon.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15)

    # Add polygon for kelurahan boundaries (handle MultiPolygon)
    if kelurahan_polygon.geom_type == 'MultiPolygon':
        for polygon in kelurahan_polygon.geoms:  # Iterate over individual polygons
            polygon_coords = np.array(polygon.exterior.coords)
            folium.Polygon(
                locations=[(lat, lng) for lng, lat in polygon_coords],
                color="blue", fill=True, fill_color="lightblue", fill_opacity=0.5
            ).add_to(m)
    else:
        polygon_coords = np.array(kelurahan_polygon.exterior.coords)
        folium.Polygon(
            locations=[(lat, lng) for lng, lat in polygon_coords],
            color="blue", fill=True, fill_color="lightblue", fill_opacity=0.5
        ).add_to(m)

    # Add circles to the map
    for center, radius in placed_circles:
        folium.Circle(
            location=[center.y, center.x],
            radius=SEARCH_RADIUS,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.3
        ).add_to(m)

    # Add markers for places found by Google Places API
    for result in results_all:
        folium.Marker(
            location=(result["lat"], result["lng"]),
            popup=f"{result['name']} - {result['address']}",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)

    # Save map as HTML file
    html_filename = os.path.join(OUTPUT_FOLDER, f"{kelurahan_name}_map_2.html")
    m.save(html_filename)
    print(f"\n✅ Map saved in: {html_filename}")
