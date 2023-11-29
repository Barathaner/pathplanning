import pygame
import sys


class CoverageView:
    def __init__(self, model):
        self.model = model
        self.grid_size = 100  # Größe des Rasters
        self.cell_size = 5  # Größe der Zellen
        self.width, self.height = (
            self.grid_size * self.cell_size,
            self.grid_size * self.cell_size,
        )
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.draw_polygon()
        pygame.display.set_caption("Polygonzeichner")

    def draw_polygon(self):
        self.screen.fill((255, 255, 255))

        # Draw the vertices with larger red circles
        for vertex in self.model.vertices:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (
                    vertex[0] * self.cell_size + self.cell_size // 2,
                    vertex[1] * self.cell_size + self.cell_size // 2,
                ),
                self.cell_size,
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
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.cell_size // 2,
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
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.cell_size // 2,
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
                    vertex[0] * self.cell_size,
                    vertex[1] * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                ),
            )

        # Draw the path connecting the vertices with blue lines
        for i in range(len(self.model.path) - 1):
            pygame.draw.line(
                self.screen,
                (0, 0, 255),
                (
                    self.model.path[i][0] * self.cell_size,
                    self.model.path[i][1] * self.cell_size,
                ),
                (
                    self.model.path[i + 1][0] * self.cell_size,
                    self.model.path[i + 1][1] * self.cell_size,
                ),
                2,
            )

        pygame.display.flip()

    def show(self):
        while True:
            self.handle_events()
            pygame.display.update()
            self.clock.tick(30)  # Adjust the frames per second as needed

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                cell_x, cell_y = x // self.cell_size, y // self.cell_size
                self.model.add_vertex((cell_x, cell_y))
                self.draw_polygon()
