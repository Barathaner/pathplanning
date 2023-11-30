import numpy as np
import shapely.geometry as geom
import heapq
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class AgentModel:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.position = Point(x, y)

class PolygonModel:
    def __init__(self):
        self.nodes = []

    def add_node(self, x,y):
        self.nodes.append(Point(x,y))
        self.sort_nodes()
        
    def sort_nodes(self):
        if len(self.nodes) > 2:
            centroid = self.calculate_centroid()
            self.nodes.sort(key=lambda point: self.calculate_angle(point, centroid), reverse=True)


    def calculate_centroid(self):
        x = sum(point.x for point in self.nodes) / len(self.nodes)
        y = sum(point.y for point in self.nodes) / len(self.nodes)
        return Point(int(x), int(y))

    def calculate_angle(self, point, centroid):
        return math.atan2(point.y - centroid.y, point.x - centroid.x)

    def get_nodes(self):
        return self.nodes
    
    
class PathPlanner:
    def __init__(self):
        self.polygon = PolygonModel()
        self.intersectedpolygon = PolygonModel()
        self.coveragepath = [Point(5,5), Point(10,5), Point(20,4), Point(20,8), Point(30,5)]
        self.agent = None
        
    def intersect_polygon(self):
        pass
    
    
    def heuristic(self, a, b):
        pass
    
    def astar(self, start, goal):
        pass
    
    def plan_coverage_path(self):
        if len(self.polygon.get_nodes()) < 3:
            print("Nicht genügend Punkte für ein Polygon.")
            return
        self.intersectedpolygon = self.intersect_polygon()
        
        self.coveragepath= self.astar(self.agent.position, self.intersectedpolygon)
class Model:
    def __init__(self):
        self.Polygon = PolygonModel()
        self.agent = None
        self.pathplanner = PathPlanner()
        
    def create_agent(self, width, height, x, y):
        self.agent = AgentModel(width, height, x, y)
        
