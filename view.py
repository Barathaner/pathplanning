from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPolygonF, QPen, QColor

class PolygonView(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.scene.setSceneRect(0, 0, 400, 400)

        self.setWindowTitle("Polygon Drawer")
        self.setGeometry(100, 100, 500, 500)

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.mousePressEvent

    def mousePressEvent(self, event):
        # Umwandlung der Mausposition in Szenen-Koordinaten
        scenePos = self.view.mapToScene(event.pos())

        x = scenePos.x()
        y = scenePos.y()
        self.controller.add_vertex(x, y)


    def draw_polygon(self, vertices):
        self.scene.clear()  # Klären Sie die Szene, bevor Sie neu zeichnen

        if vertices:
            # Erstellen eines QPolygonF-Objekts mit den Vertex-Koordinaten
            polygon = QPolygonF(vertices)

            pen = QPen(QColor(Qt.red))
            self.scene.addPolygon(polygon, pen)

