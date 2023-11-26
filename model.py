class CoverageModel:
    def __init__(self):
        self.vertices = []
        self.path = []
        self.agent_size = None
        self.agent_position = None

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def calculate_path(self):
        if len(self.vertices) < 3:
            return
        self.path = self.vertices + [self.vertices[0]]
    # Hinzufügen einer Methode zum Entfernen des letzten Punktes
    def remove_last_vertex(self):
        if self.vertices:
            self.vertices.pop()
    
