import json
from shapely.geometry import Point, Polygon, MultiPolygon

# Load the JSON data
with open("detailed_ciumbuleuit.json", "r") as file:
    data = json.load(file)

# Extract and validate the polygons
coordinates = data["coordinates"]
polygons = [Polygon(p[0]) for p in coordinates]

# Convert to MultiPolygon and fix precision issues
multipolygon = MultiPolygon(polygons).buffer(0)

# Function to check if a point is inside
def is_point_inside_ciumbuleuit(latitude, longitude):
    point = Point(longitude, latitude)  # Order: (x, y) = (longitude, latitude)
    return multipolygon.contains(point)

# Example usage
latitude = -6.85784  # Replace with your latitude
longitude = 107.61277  # Replace with your longitude

if is_point_inside_ciumbuleuit(latitude, longitude):
    print("The point is INSIDE Ciumbuleuit.")
else:
    print("The point is OUTSIDE Ciumbuleuit.")
