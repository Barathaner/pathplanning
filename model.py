class CoverageModel:
    def __init__(self):
        self.vertices = []
        self.path = []

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
