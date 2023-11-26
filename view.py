import matplotlib.pyplot as plt
import matplotlib.patches as patches

class CoverageView:
    def __init__(self, model):
        self.model = model
        self.fig, self.ax = plt.subplots()

    def draw_polygon(self):
        self.ax.clear()
        polygon = patches.Polygon(self.model.vertices, closed=True, fill=False)
        self.ax.add_patch(polygon)
        self.fig.canvas.draw()

    def draw_path(self):
        self.ax.plot(*zip(*self.model.path), marker='o', color='blue')
        self.fig.canvas.draw()

    def show(self):
        plt.show()
    
    
