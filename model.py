import numpy as np
import shapely.geometry as geom
import heapq
import math


class Point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)


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
        self.intersectedpolygon = []
        self.agent_path = []
        self.agent = None
        self.shapely_polygon = None  # Hinzugefügtes Attribut für das shapely Polygon


    
    def create_agent(self, width, height, x, y):
        self.agent = AgentModel(width, height, x, y)

    
    def plan_intersectedpolygon(self):
        self.intersectedpolygon = []
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
            
            # Überprüfen, ob das Ergebnis ein Polygon oder ein MultiPolygon ist
            if isinstance(intersected_strip, geom.Polygon):
                for i in intersected_strip.exterior.coords:
                    print(i)
                    self.intersectedpolygon.append(Point(int(math.floor(i[0])), int(math.floor(i[1]))))
            elif isinstance(intersected_strip, geom.MultiPolygon):
                for polygon in intersected_strip.geoms:
                    for i in polygon.exterior.coords:
                        print(i)
                        self.intersectedpolygon.append(Point(int(math.floor(i[0])), int(math.floor(i[1]))))

            # Berechne den Pfad innerhalb des Streifens
            current_x += self.agent.width


    def heuristic(self, a, b):
        # Konvertieren Sie beide Punkte in numpy Arrays für die Berechnung
        a_array = np.array([a[0], a[1]])
        b_array = np.array([b[0], b[1]])
        return np.linalg.norm(a_array - b_array)

    def plan_coverage_agent_path(self):
        self.agent_path = []
        self.plan_intersectedpolygon()

        if not self.intersectedpolygon:
            return

        raw_agent_path = []
        start = (self.agent.position.x, self.agent.position.y)
        for goal_point in self.intersectedpolygon:
            goal = (goal_point.x, goal_point.y)
            path_segment = self.a_star_search(start, goal)
            raw_agent_path.extend(path_segment)
            start = goal

        # Duplikate entfernen
        self.agent_path = []
        for point in raw_agent_path:
            self.agent_path.append(point)


    def a_star_search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1  # oder eine spezifische Kostenfunktion
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, goal)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        # Rekonstruieren Sie den Pfad von start zu goal
        path = []
        while current != start:
            path.append(Point(current[0], current[1]))
            current = came_from[current]
        path.append(Point(start[0],start[1]))  # optional
        path.reverse()  # optional
        
        return path


    def get_neighbors(self, node):
        """Bestimmt die Nachbarn eines Knotens im Raster."""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1),(-1,-1),(1,1)]  # 4-Wege-Nachbarschaft
        neighbors = []
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            # Überprüfen Sie hier, ob der Nachbar innerhalb der Grenzen und nicht blockiert ist.
            neighbors.append(neighbor)
        return neighbors
