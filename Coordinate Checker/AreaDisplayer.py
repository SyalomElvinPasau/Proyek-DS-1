import json
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

# Load the JSON data
with open("ciumbuleuit.json", "r") as file:
    data = json.load(file)

# Validate that the JSON contains a Polygon
if data["type"] != "Polygon":
    raise ValueError("The provided JSON file does not contain a Polygon.")

# Extract the outer boundary of the Polygon
coordinates = data["coordinates"][0]  # Extract the first (outer) ring

# Create a Polygon object
polygon = Polygon(coordinates).buffer(0)  # Fix precision issues

# Function to check if a point is inside
def is_point_inside_area(latitude, longitude):
    point = Point(longitude, latitude)  # Order: (x, y) = (longitude, latitude)
    return polygon.contains(point)

# Example test point
latitude = -6.8570  # Change this to test other points
longitude = 107.6090
point = Point(longitude, latitude)

# Plot the polygon
fig, ax = plt.subplots(figsize=(8, 8))

# Extract coordinates for plotting
x, y = polygon.exterior.xy
ax.plot(x, y, "b-", linewidth=1)  # Blue outline
ax.fill(x, y, "cyan", alpha=0.4)  # Light blue fill

# Plot the test point
color = "green" if is_point_inside_area(latitude, longitude) else "red"
ax.plot(point.x, point.y, "o", color=color, markersize=8, label="Test Point")

# Labels and display
ax.set_title("Ciumbuleuit Area (Polygon)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.legend(["Ciumbuleuit Boundary", "Test Point (Green=Inside, Red=Outside)"])
plt.grid(True)
plt.show()
