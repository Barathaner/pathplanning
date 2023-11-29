from PyQt5.QtCore import QPointF

class PolygonController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_vertex(self, x, y):
        self.model.add_vertex(QPointF(x, y))
        self.view.draw_polygon(self.model.get_vertices())
