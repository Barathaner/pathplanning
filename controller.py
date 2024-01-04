# controller.py
from view import PolygonView
from view import WelcomeView


class PolygonController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_vertex(self, x, y):
        self.model.polygon.add_node(x, y)
        self.view.draw_polygon(self.model.polygon.get_nodes())

    def create_agent(self, width, height, x, y):
        self.model.create_agent(width, height, x, y)
        self.view.draw_agent(self.model.agent)

    def remove_agent(self):
        self.model.remove_agent()
        self.view.draw_agent(self.model.agent)

    def reset_grid(self):
        self.view.close()
        self.model.reset_model()
        self.controller = PolygonController(self.model, None)
        self.view = PolygonView(self.controller)
        self.controller.view = self.view
        self.view.show()

    def handle_enter_pressed(self):
        if isinstance(self.view, WelcomeView):
            # Rufen Sie die Methode in WelcomeView auf, um das Pathplanning zu starten
            self.view.start_pathplanning()

        elif isinstance(self.view, PolygonView):
            self.model.plan_coverage_agent_path()

            if self.view.show_agent_path_checkbox.isChecked():
                path_to_draw = self.model.agent_path
            elif self.view.show_coverage_path_checkbox.isChecked():
                path_to_draw = self.model.coverage_path
            else:
                # Default to agent path if neither checkbox is checked
                path_to_draw = self.model.agent_path

            self.view.draw_polygons(self.model.grid)
            self.view.draw_path(path_to_draw)

    def start_pathplanning(self, agent_width, agent_height, agent_x, agent_y):
        # Erstelle den PolygonController und die PolygonView
        polygon_controller = PolygonController(self.model, None)
        polygon_view = PolygonView(polygon_controller)
        polygon_controller.view = polygon_view
        # Zeige die PolygonView an
        polygon_view.show()
        # Schließe die WelcomeView
        self.view.close()

        # Überprüfen Sie, ob alle Eingaben vollständig sind, bevor Sie den Agenten erstellen und zeichnen
        if agent_width != 0 or agent_height != 0:
            agent_width = int(agent_width)
            agent_height = int(agent_height)
            agent_x = int(agent_x)
            agent_y = int(agent_y)

            # Erstellen und Zeichnen des Agenten in der PolygonView
            polygon_controller.create_agent(agent_width, agent_height, agent_x, agent_y)
            polygon_view.draw_agent(polygon_controller.model.agent)

        # Zeige die PolygonView an
        polygon_view.show()
