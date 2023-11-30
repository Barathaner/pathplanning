import numpy as np
import shapely.geometry as geom
import heapq
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class AgentModel:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.position = Point(x, y)

class PolygonModel:
    def __init__(self):
        self.nodes = []
        self.minx = 9999999
        self.miny = 9999999
        self.maxx = -9999999
        self.maxy = -9999999

    def add_node(self, x,y):
        self.nodes.append(Point(x,y))
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
            self.nodes.sort(key=lambda point: self.calculate_angle(point, centroid), reverse=True)


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
        return Point(int(x), int(y))

    def calculate_angle(self, point, centroid):
        return math.atan2(point.y - centroid.y, point.x - centroid.x)

    def get_nodes(self):
        return self.nodes
    
    
class Model:
    def __init__(self):
        self.polygon = PolygonModel()
        self.intersectedpolygon = PolygonModel()
        self.coveragepath = [Point(5,5), Point(10,5), Point(20,4), Point(20,8), Point(30,5)]
        self.agent = None
        
    def intersect_polygon(self):
        pass
    
    
    def create_agent(self, width, height, x, y):
        self.agent = AgentModel(width, height, x, y)
        
    def heuristic(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))
    
    def astar(self, start, goal):
        pass
    
    def plan_coverage_path(self):
        if len(self.polygon.get_nodes()) < 3:
            print("Nicht genügend Punkte für ein Polygon.")
            return
        
        area = self.polygon.to_shapely_polygon()
        minx, miny, maxx, maxy = area.bounds
        current_x = minx

        while current_x < maxx:
            # Erstelle einen Streifen
            strip_polygon = geom.Polygon([(current_x, miny), (current_x + self.agent.width, miny), 
                                        (current_x + self.agent.width, maxy), (current_x, maxy)])
            intersected_strip = area.intersection(strip_polygon)

            if intersected_strip.is_empty:
                current_x += self.agent.width
                continue

            if isinstance(intersected_strip, geom.Polygon):
                for i in intersected_strip.exterior.coords:
                    print(i)
            elif isinstance(intersected_strip, geom.MultiPolygon):
                for poly in intersected_strip:
                    for i in poly.exterior.coords:
                        print(i)

            current_x += self.agent.width
