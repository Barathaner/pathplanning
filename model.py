import numpy as np
import shapely.geometry as geom
import heapq


class AgentModel:
    def __init__(self,width,height,x,y):
        self.width=width
        self.height=height
        self.x=x
        self.y=y
        
    def move(self,x,y):
        self.x=x
        self.y=y
        

class CoverageModel:
    def __init__(self):
        self.vertices = []
        self.agent = None
        self.coverage_path = []  # Initialisiere die Variable für den Pfad
        self.agent_path = []
        self.path = []
        self.map = [500, 500]
        
    def add_agent(self, w, h, x, y):
        self.agent = AgentModel(w, h, x, y)

    def updateAgentPosition(self, x, y):
        self.agent.move(x, y)

    def add_edges(self, edge):
        self.edges.append(edge)
        
    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def remove_last_vertex(self):
        if self.vertices:
            self.vertices.pop()

    def close_polygon(self):
        if len(self.vertices) > 2:
            # Schließe das Polygon
            self.path = self.vertices.copy()
            self.path.append(self.vertices[0])
            self.vertices.append(
                self.vertices[0]
            )  # Füge den ersten Punkt am Ende hinzu

    def reset(self):
        self.vertices = []
        self.path = []

    def get_points(self):
        return self.vertices

    def get_points_as_array(self):
        return [list(point) for point in self.vertices]

    def is_polygon_closed(self):
        return len(self.path) > 1



    def generate_path(self):
        # Stelle sicher, dass genügend Punkte für ein Polygon vorhanden sind
        if len(self.polygon) < 3:
            print("Nicht genügend Punkte für ein Polygon.")
            return

        # Erstelle ein Polygon aus den Punkten
        area = geom.Polygon(self.polygon)
        minx, miny, maxx, maxy = area.bounds
        current_x = minx

        while current_x < maxx:
            # Erstelle einen Streifen
            strip_polygon = geom.Polygon([(current_x, miny), (current_x + self.agent.width, miny), 
                                          (current_x + self.agent.width, maxy), (current_x, maxy)])
            intersected_strip = area.intersection(strip_polygon)
            
            for i in intersected_strip.exterior.coords:
                print(i)
                self.coverage_path.append(i)   

            # Berechne den Pfad innerhalb des Streifens

            current_x += self.agent.width

            
    def calculate_strip_path(self, strip):
        """
        Berechnet einen Pfad innerhalb eines gegebenen Streifens in einem Zickzack-Muster.
        """
        if not self.agent:
            raise ValueError("Agent muss vor der Pfadberechnung hinzugefügt werden")

        x, y = strip.exterior.coords.xy
        if len(set(zip(x, y))) < 3:
            print("Warnung: Streifen hat nicht genügend einzigartige Punkte.")
            return
        punkte = list(zip(x, y))
        punkte.sort(key=lambda p: p[0])  # Sortiere nach x-Koordinate

        # Pfad für diesen Streifen generieren
        strip_path = []
        for i in range(len(punkte)):
            if i % 2 == 0:
                # Aufsteigende Y-Koordinaten
                y_sorted = sorted(punkte, key=lambda p: p[1])
            else:
                # Absteigende Y-Koordinaten
                y_sorted = sorted(punkte, key=lambda p: p[1], reverse=True)

            for p in y_sorted:
                strip_path.append(p)

        # Speichere den Pfad
        self.coverage_path.extend(strip_path)
    
    def heuristic(self, a, b):
        """Schätzt die Distanz zwischen zwei Punkten."""
        return np.linalg.norm(np.array(a) - np.array(b))
    
    
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
            path.append(current)
            current = came_from[current]
        path.append(start)  # optional
        path.reverse()  # optional
        
        return path

    
    
    def plan_coverage_path(self):
        """Plant den Pfad des Agenten durch alle Punkte in coverage_path."""
        if not self.coverage_path:
            return

        agent_path = []
        start = (self.agent.x, self.agent.y)
        for goal in self.coverage_path:
            path_segment = self.a_star_search(start, goal)
            agent_path.extend(path_segment)
            start = goal
        self.agent_path = agent_path
    
    def get_neighbors(self, node):
        """Bestimmt die Nachbarn eines Knotens im Raster."""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # 4-Wege-Nachbarschaft
        neighbors = []
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            # Überprüfen Sie hier, ob der Nachbar innerhalb der Grenzen und nicht blockiert ist.
            neighbors.append(neighbor)
        return neighbors
