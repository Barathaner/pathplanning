from PyQt5.QtCore import QPointF

class PolygonController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_vertex(self, x, y):
        self.model.add_vertex(QPointF(x, y))
        self.view.draw_polygon(self.model.get_vertices())

    def handle_enter_pressed(self):
        self.model.plan_coverage_path()
        self.view.draw_path(self.model.agent_path)

    def create_agent(self, width, height, x, y):
        self.model.create_agent(width, height, x, y)
        self.view.draw_agent(self.model.agent)
