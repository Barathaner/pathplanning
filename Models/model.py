import numpy as np
import shapely.geometry as geom
import heapq
from Models.polygon import PolygonModel
from Models.agent import AgentModel


class Model:
    def __init__(self):
        self.polygon = PolygonModel()
        self.agent = None
        self.grid = []
        self.gridrects = []
        self.coverage_path = []
        self.agent_path = []
        self.isinfield = False
        self.shapely_polygon = None  # Hinzugefügtes Attribut für das shapely Polygon
        self.reset_model()

    def create_agent(self, width, height, x, y):
        try:
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive numbers.")
            self.agent = AgentModel(width, height, x, y)
        except Exception as e:
            print(f"Error in create_agent: {e}")
            self.agent = None

    def reset_model(self):
        self.polygon = PolygonModel()
        self.coverage_path = []
        self.agent_path = []
        self.agent = None
        self.isinfield = False
        self.grid = []
        self.shapely_polygon = None
        
    def convert_tuple_to_point(self):
        try:
            newpath = [geom.Point(p[0], p[1]) for p in self.coverage_path if isinstance(p, tuple) and len(p) == 2]
            self.coverage_path = newpath
        except Exception as e:
            print(f"Error in convert_tuple_to_point: {e}")

            
    def plan_coverage_agent_path(self):
        try:
            self.agent_path = []
            self.create_grid_for_polygon()
            self.generate_waypoints()
            self.agent_path = self.a_star_search(
                (self.agent.position.x, self.agent.position.y),
                (self.coverage_path[0].x, self.coverage_path[0].y),
            )
            self.isinfield = True
            for i in range(len(self.coverage_path) - 1):
                self.agent_path += self.a_star_search(
                    (self.coverage_path[i].x, self.coverage_path[i].y),
                    (self.coverage_path[i + 1].x, self.coverage_path[i + 1].y),
                )
            self.isinfield = False
        except Exception as e:
            print(f"Error in plan_coverage_agent_path: {e}")

    def create_grid_for_polygon(self):
        polygon = self.polygon.to_shapely_polygon()
        minx, miny, maxx, maxy = polygon.bounds
        grid = []

        y = miny
        while y <= maxy:
            x = minx
            while x <= maxx:
                rect = geom.box(x, y, x + self.agent.width,
                                y + self.agent.height)
                if polygon.contains(rect):
                    grid.append(rect)
                x += 1
            y += 1

        self.grid = grid



    def generate_waypoints(self):
        self.coverage_path = []

        # Sortiere die Rechtecke nach Y und dann nach X
        sorted_rects = sorted(
            self.grid, key=lambda r: (r.bounds[1], r.bounds[0]))

        current_y = None
        row_rects = []
        reverse = False

        for rect in sorted_rects:
            rect_y = rect.bounds[1]

            if current_y is None:
                current_y = rect_y

            if rect_y != current_y:
                self.process_row(row_rects, reverse)
                row_rects = [rect]
                current_y = rect_y
                reverse = not reverse
            else:
                row_rects.append(rect)

        # Verarbeite die letzte Zeile
        if row_rects:
            self.process_row(row_rects, reverse)

    def process_row(self, row_rects, reverse):
        try:
            if not row_rects:
                return

            if reverse:
                row_rects.reverse()

            # Füge den Anfangspunkt der Zeile hinzu
            first_rect = row_rects[0]
            self.coverage_path.append(geom.Point(
                first_rect.bounds[0], first_rect.bounds[1]))

            # Füge den Endpunkt der Zeile hinzu
            last_rect = row_rects[-1]
            self.coverage_path.append(geom.Point(
                last_rect.bounds[0], last_rect.bounds[1]))
        except Exception as e:
            print(f"Error in process_row: {e}")

    def heuristic(self, a, b):

        agent_rect = geom.box(a[0], a[1],
                              a[0] + self.agent.width,
                              a[1] + self.agent.height)

        if not self.polygon.to_shapely_polygon().contains(agent_rect) and self.isinfield:
            return 99999999999
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
                new_cost = cost_so_far[current] + self.heuristic(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, goal)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        # Rekonstruieren Sie den Pfad von start zu goal
        path = []
        while current != start:
            path.append(geom.Point(current[0], current[1]))
            current = came_from[current]
        path.reverse()  # optional

        return path

    def get_neighbors(self, node):
        try:
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1),
                        (-1, -1), (1, 1), (-1, 1), (1, -1)]  # Erweiterte 8-Wege-Nachbarschaft
            neighbors = []

            for direction in directions:
                neighbor_x, neighbor_y = (
                    node[0] + direction[0], node[1] + direction[1])

                neighbors.append((neighbor_x, neighbor_y))

            return neighbors
        except Exception as e:
            print(f"Error in get_neighbors: {e}")
            return []
