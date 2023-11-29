import pygame
import sys


class CoverageView:
    def __init__(self, model):
        self.model = model
        self.screen = pygame.display.set_mode((self.model.map[0], self.model.map[1]))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Polygonzeichner")

    def draw_polygon(self):
        self.screen.fill((255, 255, 255))

        # Draw the vertices with larger red circles
        for vertex in self.model.vertices:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (
                    vertex[0],
                    vertex[1]
                ),5
            )

        # Connect the vertices with red lines
        if len(self.model.vertices) > 1:
            if self.model.is_polygon_closed():
                # Wenn das Polygon geschlossen ist, zeichne den Pfad
                pygame.draw.lines(
                    self.screen,
                    (255, 0, 0),
                    False,
                    [
                        (
                            x ,
                            y ,
                        )
                        for x, y in self.model.path
                    ],
                    2,
                )
            else:
                # Wenn das Polygon nicht geschlossen ist, zeichne die Kanten zwischen den Vertices
                pygame.draw.lines(
                    self.screen,
                    (255, 0, 0),
                    False,
                    [
                        (
                            x ,
                            y ,
                        )
                        for x, y in self.model.vertices
                    ],
                    2,
                )

        pygame.display.flip()

    def draw_path(self):
        self.screen.fill((255, 255, 255))

        # Draw the vertices
        for vertex in self.model.vertices:
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                (
                    vertex[0] ,
                    vertex[1] 
                ),
            )

        # Draw the path connecting the vertices with blue lines
        for i in range(len(self.model.path) - 1):
            pygame.draw.line(
                self.screen,
                (0, 0, 255),
                (
                    self.model.path[i][0] ,
                    self.model.path[i][1] ,
                ),
                (
                    self.model.path[i + 1][0] ,
                    self.model.path[i + 1][1] ,
                ),
                2,
            )

        pygame.display.flip()

    def show(self):
        self.screen.fill((255, 255, 255))
        pygame.display.flip()

        # Hier können Sie Logik hinzufügen, um zu entscheiden,
        # ob draw_polygon oder draw_path aufgerufen werden soll
        self.draw_polygon()  # oder self.draw_path()

        pygame.display.update()
        self.clock.tick(30)  # Adjust the frames per second as needed
