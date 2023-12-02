from model import Model
from view import PolygonView


class PolygonController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_vertex(self, x, y):
        self.model.polygon.add_node(x, y)
        self.view.draw_polygon(self.model.polygon.get_nodes())

    def handle_enter_pressed(self):
        self.model.plan_coverage_agent_path()
        self.view.draw_polygons(self.model.gridrects)
        self.view.draw_path(self.model.agent_path)

    def create_agent(self, width, height, x, y):
        self.model.create_agent(width, height, x, y)
        self.view.draw_agent(self.model.agent)

    def remove_agent(self):
        self.model.remove_agent()
        self.view.draw_agent(self.model.agent)

    def reset_grid(self):
        self.view.close()
        self.model = Model()
        self.controller = PolygonController(self.model, None)
        self.view = PolygonView(self.controller)
        self.controller.view = self.view
        self.view.show()


class WelcomeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def handle_enter_pressed(self):
        print("Enter pressed")

    def create_agent(self, width, height, x, y):
        self.model.create_agent(width, height, x, y)
