import json
from shapely.geometry import Point, Polygon

# Load the JSON data
with open("ciumbuleuit.json", "r") as file:
    data = json.load(file)

# Validate that the JSON contains a Polygon
if data["type"] != "Polygon":
    raise ValueError("The provided JSON file does not contain a Polygon.")

# Extract the outer boundary of the Polygon
coordinates = data["coordinates"][0]  # The first list contains the outer ring

# Create a Polygon object
polygon = Polygon(coordinates).buffer(0)  # Fix precision issues

# Function to check if a point is inside the polygon
def is_point_inside_area(latitude, longitude):
    point = Point(longitude, latitude)  # Order: (x, y) = (longitude, latitude)
    return polygon.contains(point)

# Example usage
latitude = -6.85784  # Replace with your latitude
longitude = 107.61277  # Replace with your longitude

if is_point_inside_area(latitude, longitude):
    print("The point is INSIDE the area.")
else:
    print("The point is OUTSIDE the area.")
