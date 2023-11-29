import pygame
import sys


class CoverageController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.polygon_closed = False
        self.first_click_point = None  # Koordinaten des ersten angeklickten Punktes

    def handle_events(self):
        # Im CoverageController
        points_array = self.model.get_points_as_array()
        print(points_array)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                print(self.polygon_closed)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and not self.polygon_closed:
                    self.model.remove_last_vertex()
                    self.view.draw_polygon()
                elif event.key == pygame.K_RETURN and not self.polygon_closed:
                    # Enter-Taste gedrückt, schließe das Polygon
                    self.model.close_polygon()
                    self.view.draw_polygon()
                    self.polygon_closed = True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.polygon_closed:
                x, y = event.pos

                if self.first_click_point is None:
                    # Erster Klick, speichere die Koordinaten
                    self.first_click_point = (x, y)
                    self.model.add_vertex((x, y))
                    self.view.draw_polygon()
                else:
                    # Zweiter Klick, überprüfe, ob es sich um den ersten Punkt handelt
                    if (x, y) == self.first_click_point:
                        self.model.close_polygon()
                        self.view.draw_polygon()
                        self.polygon_closed = True
                        self.first_click_point = (
                            None  # Zurücksetzen für zukünftige Polygone
                        )
                    else:
                        self.model.add_vertex((x, y))
                        self.view.draw_polygon()

    def run(self):
        while True:
            self.handle_events()




    def add_agent(self,w,h, x, y):
        self.model.add_agent(w,h,x, y)
        

    def move_agent(self, x, y):
        self.model.updateAgentPosition(x, y)
        self.view.show()

    def generate_path(self):
        self.model.generate_path()
        self.view.show()

    def plan_agent_path(self):
        self.model.plan_coverage_path()
        self.view.showagentpath()
