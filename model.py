import numpy as np
import shapely.geometry as geom
import heapq
from PyQt5.QtCore import QPointF

class Agent:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.position = QPointF(x, y)

class PolygonModel:
    def __init__(self):
        self.vertices = []
        self.agent = None
        self.coverage_path = []  # Pfad für die Abdeckung
        self.agent_path = []     # Pfad des Agenten

    def add_vertex(self, point):
        self.vertices.append(point)

    def get_vertices(self):
        return self.vertices

    def create_agent(self, width, height, x, y):
        self.agent = Agent(width, height, x, y)

    def plan_coverage_path(self):
        if not self.vertices or not self.agent:
            print("Polygon oder Agent nicht definiert.")
            return

        # Erstelle ein Polygon aus den Punkten
        area = geom.Polygon([(v.x(), v.y()) for v in self.vertices])
        minx, miny, maxx, maxy = area.bounds
        current_x = minx

        while current_x < maxx:
            strip_polygon = geom.Polygon([(current_x, miny), 
                                          (current_x + self.agent.width, miny), 
                                          (current_x + self.agent.width, maxy), 
                                          (current_x, maxy)])
            intersected_strip = area.intersection(strip_polygon)
            
            if intersected_strip.is_empty:
                current_x += self.agent.width
                continue

            if hasattr(intersected_strip, 'exterior'):
                for i in intersected_strip.exterior.coords:
                    self.coverage_path.append(i)

            current_x += self.agent.width

        self.agent_path = self.a_star_search(self.agent.position, self.coverage_path[0]) if self.coverage_path else []

    def heuristic(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def a_star_search(self, start, goal):
        start = (start.x(), start.y())
        
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in self.get_neighbors(QPointF(*current)):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, goal)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()

        return [QPointF(x, y) for x, y in path]




    def get_neighbors(self, node):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        neighbors = []
        for direction in directions:
            neighbor = (node.x() + direction[0], node.y() + direction[1])
            neighbors.append(QPointF(*neighbor))
        return neighbors
