from shapely.geometry import Point as P
class AgentModel:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.position = P(x, y)
