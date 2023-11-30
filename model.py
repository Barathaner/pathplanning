import numpy as np
import shapely.geometry as geom
import heapq
from PyQt5.QtCore import QPoint
import math

class AgentModel:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.position = QPoint(x, y)
        
class PolygonModel:
    def __init__(self):
        self.nodes = []

    def add_node(self, point):
        self.nodes.append(point)
        self.sort_nodes()

    def sort_nodes(self):
        if len(self.nodes) > 2:
            centroid = self.calculate_centroid()
            self.nodes.sort(key=lambda point: self.calculate_angle(point, centroid), reverse=True)

    def calculate_centroid(self):
        x = sum(point.x() for point in self.nodes) / len(self.nodes)
        y = sum(point.y() for point in self.nodes) / len(self.nodes)
        return QPoint(int(x), int(y))

    def calculate_angle(self, point, centroid):
        return math.atan2(point.y() - centroid.y(), point.x() - centroid.x())
    
    def get_nodes(self):
        return self.nodes

class Model:
    def __init__(self):
        self.Polygon = PolygonModel()
        self.agent = None
        
    def create_agent(self, width, height, x, y):
        self.agent = AgentModel(width, height, x, y)