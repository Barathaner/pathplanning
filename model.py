import numpy as np
import shapely.geometry as geom
import heapq
import math

from shapely.geometry import Point as P


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

    def add_node(self, x, y):
        self.nodes.append(Point(x, y))
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
            self.nodes.sort(key=lambda point: self.calculate_angle(
                point, centroid), reverse=True)

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
        self.coverage_path = []
        self.agent_path = []
        self.agent = None
        self.gridrects = []
        self.isinfield = False
        self.grid = []
        self.shapely_polygon = None  # Hinzugefügtes Attribut für das shapely Polygon

    def create_agent(self, width, height, x, y):
        self.agent = AgentModel(width, height, x, y)

    def create_grid_for_polygon(self):
        polygon = self.polygon.to_shapely_polygon()
        minx, miny, maxx, maxy = polygon.bounds
        grid = []

        y = miny
        while y + self.agent.height <= maxy:
            x = minx
            while x + self.agent.width <= maxx:
                rect = geom.box(x, y, x + self.agent.width,
                                y + self.agent.height)
                if polygon.contains(rect):
                    grid.append(rect)
                x += self.agent.width
            y += self.agent.height

        self.grid = grid

    def convert_tuple_to_point(self):
        newpath = []
        for p in self.coverage_path:
            p = Point(p[0], p[1])
            newpath.append(p)
        self.coverage_path = newpath

    def sort_rectangles_by_y(self, rectangles):
        """Sortiert Rechtecke nach ihrer Y-Position."""
        return sorted(rectangles, key=lambda r: r.bounds[1])

    def sort_row_by_x(self, row, direction):
        """Sortiert eine Reihe von Rechtecken nach ihrer X-Position."""
        return sorted(row, key=lambda r: r.bounds[0], reverse=(direction == "left"))

    def get_center_of_rectangle(self, rect):
        """Gibt die zentrale Position eines Rechtecks zurück, gerundet auf Ganzzahlen."""
        minx, miny, maxx, maxy = rect.bounds
        center_x = int(round((minx + maxx) / 2))
        center_y = int(round((miny + maxy) / 2))
        return center_x, center_y

    def merge_rectangles(self):
        i = 0
        while i < len(self.grid) - 1:
            rect1 = self.grid[i]
            rect2 = self.grid[i + 1]

            # Extrahiere die Grenzen der Rechtecke
            minx1, miny1, maxx1, maxy1 = rect1.bounds
            minx2, miny2, maxx2, maxy2 = rect2.bounds

            # Überprüfe, ob sie sich in der X-Richtung berühren
            if maxx1 == minx2 and (miny1 == miny2 and maxy1 == maxy2):
                # Vereinige die Rechtecke und entferne das zweite
                self.grid[i] = rect1.union(rect2)
                del self.grid[i + 1]
            else:
                i += 1
        self.gridrects = self.grid.copy()

    def find_nearest_rectangle(self, current_rect, remaining_rects):
        min_dist = float('inf')
        nearest_rect = None

        current_minx, current_miny, current_maxx, current_maxy = current_rect.bounds
        current_points = [P(current_minx, current_miny),
                          P(current_maxx, current_maxy)]

        for rect in remaining_rects:
            minx, miny, maxx, maxy = rect.bounds
            rect_points = [P(minx, miny), P(maxx, maxy)]

            for point1 in current_points:
                for point2 in rect_points:
                    dist = point1.distance(point2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_rect = rect

        return nearest_rect

    def generate_waypoints(self):
        self.coverage_path = []
        reverse = False

        while self.grid:
            rect = self.grid.pop(0)
            minx, miny, maxx, maxy = rect.bounds

            if reverse:
                
                if self.polygon.to_shapely_polygon().contains(P(maxx + self.agent.width,miny)) :
                    start_point = P(maxx, miny)
                    end_point = P(minx, miny)
                else:
                    start_point = P(maxx-self.agent.width, miny)
                    end_point = P(minx, miny)
            else:
                if self.polygon.to_shapely_polygon().contains(P(maxx + self.agent.width,miny)) :
                    start_point = P(minx, miny)
                    end_point = P(maxx, miny)
                else:
                    start_point = P(minx, miny)
                    end_point = P(maxx-self.agent.width, miny)

            if not self.coverage_path or self.coverage_path[-1].distance(start_point) > 0:
                self.coverage_path.append(start_point)

            self.coverage_path.append(end_point)

            reverse = not reverse

            if self.grid:
                next_rect = self.find_nearest_rectangle(rect, self.grid)
                self.grid.remove(next_rect)
                self.grid.insert(0, next_rect)

    def plan_coverage_agent_path(self):
        self.agent_path = []
        self.create_grid_for_polygon()
        self.merge_rectangles()
        self.generate_waypoints()
        self.agent_path = self.a_star_search(
            (self.agent.position.x, self.agent.position.y), (self.coverage_path[0].x, self.coverage_path[0].y))
        self.isinfield = True
        for i in range(len(self.coverage_path)-1):
            self.agent_path += self.a_star_search(
                (self.coverage_path[i].x, self.coverage_path[i].y), (self.coverage_path[i+1].x, self.coverage_path[i+1].y))
        self.isinfield = False

    def heuristic(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

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
                # oder eine spezifische Kostenfunktion
                new_cost = cost_so_far[current] + 1
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
        path.append(Point(start[0], start[1]))  # optional
        path.reverse()  # optional

        return path

    def get_neighbors(self, node):
        """Bestimmt die Nachbarn eines Knotens im Raster."""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1),
                      (-1, -1), (1, 1)]  # 4-Wege-Nachbarschaft
        neighbors = []
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            neighbor_point = P(neighbor[0], neighbor[1])

            if self.polygon.to_shapely_polygon().intersects(neighbor_point) or not self.isinfield:
                neighbors.append(neighbor)
        return neighbors

