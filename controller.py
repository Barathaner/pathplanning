class CoverageController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.fig = view.fig

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Binden einer Tastatureingabe für das Rückgängigmachen
        self.kid = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self, event):
        if event.key == 'z':  # Beispielsweise Rückgängig mit 'Z'
            self.model.remove_last_vertex()
            self.view.draw_polygon()

    def on_click(self, event):
        if event.dblclick:
            self.model.calculate_path()
            self.view.draw_path()
            self.fig.canvas.mpl_disconnect(self.cid)
        else:
            self.model.add_vertex((event.xdata, event.ydata))
            self.view.draw_polygon()
