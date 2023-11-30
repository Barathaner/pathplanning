
class PolygonController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_vertex(self, x, y):
        self.model.polygon.add_node(x, y)
        self.view.draw_polygon(self.model.polygon.get_nodes())

    def handle_enter_pressed(self):
        self.model.plan_coverage_path()
        self.view.draw_path(self.model.coveragepath)

    def create_agent(self, width, height, x, y):
        self.model.create_agent(width, height, x, y)
        self.view.draw_agent(self.model.agent)
