import json
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPolygon

# Load the JSON data
with open("detailed_ciumbuleuit.json", "r") as file:
    data = json.load(file)

# Extract coordinates (handling MultiPolygon)
coordinates = data["coordinates"]
polygons = [Polygon(p[0]) for p in coordinates]  # Convert to shapely Polygon
multipolygon = MultiPolygon(polygons)

# Function to check if a point is inside
def is_point_inside_ciumbuleuit(latitude, longitude):
    point = Point(longitude, latitude)  # Shapely uses (x, y) => (longitude, latitude)
    return multipolygon.contains(point)

# Example test point
latitude = -6.85840  # Change this to test other points
longitude = 107.61278
point = Point(longitude, latitude)

# Plot the multipolygon
fig, ax = plt.subplots(figsize=(8, 8))

# Plot each polygon in the MultiPolygon
for polygon in multipolygon.geoms:
    x, y = polygon.exterior.xy
    ax.plot(x, y, "b-", linewidth=1)  # Blue outline
    ax.fill(x, y, "cyan", alpha=0.4)  # Light blue fill

# Plot the test point
color = "green" if is_point_inside_ciumbuleuit(latitude, longitude) else "red"
ax.plot(point.x, point.y, "o", color=color, markersize=8, label="Test Point")

# Labels and display
ax.set_title("Ciumbuleuit Area")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.legend(["Ciumbuleuit Boundary", "Test Point (Green=Inside, Red=Outside)"])
plt.grid(True)
plt.show()
