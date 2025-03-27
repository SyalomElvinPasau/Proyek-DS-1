import json
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from matplotlib.patches import Polygon, Circle

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Komen yg ada awalan !! baca, antara penting atau bagian yg bisa diatur confignya
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Load Polygon (Kelurahan boundary)
GEOJSON_PATH = "C:/Users/Alief/Documents/ProyekDS/Proyek-DS-1/GADM/kelurahan_bandung.geojson"
with open(GEOJSON_PATH) as f:
    geojson_data = json.load(f)

kelurahan_data = geojson_data["features"][0]  # !!Sementara ini ngambil kelurahan pertama doang, kalau mau satu bandung gapapa
kelurahan_polygon = shape(kelurahan_data["geometry"])
bounds = kelurahan_polygon.bounds

# Define Hexagonal Grid Parameters
polygon_width = bounds[2] - bounds[0]
polygon_height = bounds[3] - bounds[1]
CIRCLE_RADIUS = min(polygon_width, polygon_height) / 30  # !!NGatur ukuran lingkaran
HEX_WIDTH = 2 * CIRCLE_RADIUS  # Horizontal spacing
HEX_HEIGHT = np.sqrt(3) * CIRCLE_RADIUS  # Vertical spacing

# Store placed circles
placed_circles = []
circle_shapes = []

# Generate hexagonal grid of points
x_min, y_min, x_max, y_max = bounds
x_vals = np.arange(x_min, x_max, HEX_WIDTH * 0.9)  # !!Ngatur lebar lingkaran buat adjustment barangkali overapping
y_vals = np.arange(y_min, y_max, HEX_HEIGHT * 1.1) # !!Ngatur tinggi lingkaran, fungsinya sama

for i, x in enumerate(x_vals):
    for j, y in enumerate(y_vals):
        if i % 2 == 1:  # Stagger odd rows
            y += HEX_HEIGHT / 2

        center = Point(x, y)
        if kelurahan_polygon.contains(center):  # Ensure circle is inside polygon
            placed_circles.append((center, CIRCLE_RADIUS))
            circle_shapes.append(Point(x, y).buffer(CIRCLE_RADIUS))  # Store as Shapely circle

# Calculate Coverage
total_polygon_area = kelurahan_polygon.area
total_circle_area = unary_union(circle_shapes).area  # Union of all circles to avoid overlaps
coverage_percentage = (total_circle_area / total_polygon_area) * 100

# Debugging: Print results
print(f"Total Circles Placed: {len(placed_circles)}")
print(f"Polygon Area: {total_polygon_area:.2f}")
print(f"Total Circle Area (Non-Overlapping): {total_circle_area:.2f}")
print(f"Coverage Percentage: {coverage_percentage:.2f}%")

# Visualization
fig, ax = plt.subplots(figsize=(8, 8))

# Plot Polygon
polygon_coords = np.array(kelurahan_polygon.exterior.coords)
polygon_patch = Polygon(polygon_coords, closed=True, edgecolor='blue', facecolor='lightblue', alpha=0.5)
ax.add_patch(polygon_patch)

# Draw Circles
for center, radius in placed_circles:
    circle_patch = Circle((center.x, center.y), radius, color='red', alpha=0.5)
    ax.add_patch(circle_patch)

ax.set_xlim(bounds[0] - CIRCLE_RADIUS, bounds[2] + CIRCLE_RADIUS)
ax.set_ylim(bounds[1] - CIRCLE_RADIUS, bounds[3] + CIRCLE_RADIUS)
ax.set_aspect('equal')
plt.title(f"Hexagonal Circle Packing in Polygon\nCoverage: {coverage_percentage:.2f}%")
plt.show()
