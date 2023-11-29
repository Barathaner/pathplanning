class PolygonModel:
    def __init__(self):
        self.vertices = []

    def add_vertex(self, point):
        self.vertices.append(point)

    def get_vertices(self):
        return self.vertices
