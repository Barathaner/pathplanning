
import shapely.geometry as geom
from shapely.geometry import Point as P
import math

class PolygonModel:
    def __init__(self):
        self.nodes = []
        self.minx = 9999999
        self.miny = 9999999
        self.maxx = -9999999
        self.maxy = -9999999

    def add_node(self, x, y):
        self.nodes.append(P(x, y))
        self.update_boundaries(x, y)
        self.sort_nodes()

    def get_boundaries(self):
        return self.minx, self.miny, self.maxx, self.maxy

    def update_boundaries(self, x, y):
        # Stelle sicher, dass x und y als Ganzzahlen behandelt werden
        x, y = int(x), int(y)

        self.minx = min(self.minx, x)
        self.miny = min(self.miny, y)
        self.maxx = max(self.maxx, x)
        self.maxy = max(self.maxy, y)

    def sort_nodes(self):
        if len(self.nodes) > 2:
            centroid = self.calculate_centroid()
            self.nodes.sort(
                key=lambda point: self.calculate_angle(point, centroid), reverse=True
            )

    def to_shapely_polygon(self):
        """Konvertiert das PolygonModel in ein shapely Polygon."""
        points = [(point.x, point.y) for point in self.nodes]
        return geom.Polygon(points)

    def intersection(self, other_polygon):
        """Berechnet die Schnittmenge des Polygons mit einem anderen Polygon."""
        poly1 = self.to_shapely_polygon()
        poly2 = other_polygon.to_shapely_polygon()
        return poly1.intersection(poly2)

    def get_exterior_coordinates(self):
        """Gibt die äußeren Koordinaten des Polygons zurück."""
        shapely_poly = self.to_shapely_polygon()
        return list(shapely_poly.exterior.coords)

    def calculate_centroid(self):
        x = sum(point.x for point in self.nodes) / len(self.nodes)
        y = sum(point.y for point in self.nodes) / len(self.nodes)
        return P(int(x), int(y))

    def calculate_angle(self, point, centroid):
        return math.atan2(point.y - centroid.y, point.x - centroid.x)

    def get_nodes(self):
        return self.nodes

