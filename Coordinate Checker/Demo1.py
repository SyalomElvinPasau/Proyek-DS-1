import json
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon

# Load the JSON data
with open("C:/Users/Alief/Documents/ProyekDS/Proyek-DS-1/GADM/kelurahan_bandung.geojson", "r") as file:
    data = json.load(file)

# Extract all kelurahan features
kelurahan_list = data["features"]  # Each feature represents a kelurahan

# Function to find which Kelurahan a point belongs to
def find_kelurahan(latitude, longitude):
    point = Point(longitude, latitude)  # Shapely uses (x, y) = (longitude, latitude)

    for kelurahan in kelurahan_list:
        name = kelurahan["properties"]["NAME_4"]  # Get the kelurahan name
        geometry_type = kelurahan["geometry"]["type"]
        coordinates = kelurahan["geometry"]["coordinates"]

        # Check if it's a MultiPolygon or a Polygon
        if geometry_type == "MultiPolygon":
            polygons = [Polygon(p[0]) for p in coordinates]  # Extract outer boundaries
            multipolygon = MultiPolygon(polygons).buffer(0)  # Fix precision issues
            if multipolygon.contains(point):
                return name
        elif geometry_type == "Polygon":
            polygon = Polygon(coordinates[0]).buffer(0)  # Fix precision issues
            if polygon.contains(point):
                return name

    return "Point is outside all kelurahan areas."

# Example test point
latitude = -6.9200  # Replace with your latitude
longitude = 107.6000  # Replace with your longitude

kelurahan_name = find_kelurahan(latitude, longitude)

if kelurahan_name != "Point is outside all kelurahan areas.":
    print(f"The point is inside Kelurahan: {kelurahan_name}")
else:
    print("The point is outside all kelurahan areas.")

# --- Visualization ---
fig, ax = plt.subplots(figsize=(10, 10))

# Plot each kelurahan and label it
for kelurahan in kelurahan_list:
    name = kelurahan["properties"]["NAME_4"]
    geometry_type = kelurahan["geometry"]["type"]
    coordinates = kelurahan["geometry"]["coordinates"]

    if geometry_type == "MultiPolygon":
        polygons = [Polygon(p[0]) for p in coordinates]
        multipolygon = MultiPolygon(polygons)
        for polygon in multipolygon.geoms:
            x, y = polygon.exterior.xy
            ax.plot(x, y, "b-", linewidth=1)
            ax.fill(x, y, "cyan", alpha=0.3)
        centroid = multipolygon.centroid  # Find the center of the multipolygon
    elif geometry_type == "Polygon":
        polygon = Polygon(coordinates[0])
        x, y = polygon.exterior.xy
        ax.plot(x, y, "b-", linewidth=1)
        ax.fill(x, y, "cyan", alpha=0.3)
        centroid = polygon.centroid  # Find the center of the polygon

    # Add kelurahan name at the centroid
    ax.text(centroid.x, centroid.y, name, fontsize=10, fontweight='bold', 
            ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Plot the test point
color = "green" if kelurahan_name != "Point is outside all kelurahan areas." else "red"
ax.plot(longitude, latitude, "o", color=color, markersize=8, label="Test Point")

# Labels and display
ax.set_title("Kelurahan Bandung Map")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.legend(["Kelurahan Boundary", "Test Point (Green=Inside, Red=Outside)"])
plt.grid(True)
plt.show()
