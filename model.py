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

    def add_vertex(self, point):
        self.vertices.append(point)

    def get_vertices(self):
        return self.vertices

    def create_agent(self, width, height, x, y):
        self.agent = Agent(width, height, x, y)
