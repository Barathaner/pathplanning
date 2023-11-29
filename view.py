from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsScene, QGraphicsView, 
                             QMainWindow, QApplication, QDialog, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPolygonF, QPen, QColor
class AgentInputDialog(QDialog):
    def __init__(self, parent=None):
        super(AgentInputDialog, self).__init__(parent)
        self.setWindowTitle('Agentendaten eingeben')

        self.layout = QVBoxLayout(self)

        self.labels = ['Breite', 'Höhe', 'Position X', 'Position Y']
        self.lineEdits = []
        for label in self.labels:
            self.layout.addWidget(QLabel(label))
            lineEdit = QLineEdit(self)
            self.lineEdits.append(lineEdit)
            self.layout.addWidget(lineEdit)

        self.okButton = QPushButton('OK', self)
        self.okButton.clicked.connect(self.accept)
        self.layout.addWidget(self.okButton)
        self.setLayout(self.layout)

    def getValues(self):
        return [lineEdit.text() for lineEdit in self.lineEdits]


from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPolygonF, QPen, QColor

class PolygonView(QMainWindow):
    def __init__(self, controller):
        self.agent_item = None  # Grafisches Objekt für den Agenten
        self.polygon_item = None  # Grafisches Objekt für das Polygon
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.openNumbersDialog()

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.controller.handle_enter_pressed()

    def draw_polygon(self, vertices):
        self.scene.clear()  # Klären Sie die Szene, bevor Sie neu zeichnen

        if vertices:
            polygon = QPolygonF(vertices)
            pen = QPen(QColor(Qt.red))
            self.scene.addPolygon(polygon, pen)

    def draw_path(self, path):
        if path:
            for i in range(len(path) - 1):
                line = QGraphicsLineItem(path[i].x(), path[i].y(), path[i + 1].x(), path[i + 1].y())
                line.setPen(QPen(QColor(Qt.green), 2))
                self.scene.addItem(line)

    def mousePressEvent(self, event):
        scenePos = self.view.mapToScene(event.pos())
        x = scenePos.x()
        y = scenePos.y()
        self.controller.add_vertex(x, y)



    def openNumbersDialog(self):
            dialog = AgentInputDialog(self)
            if dialog.exec_():
                values = dialog.getValues()
                if len(values) == 4:
                    width, height, x, y = map(float, values)
                    self.controller.create_agent(width, height, x, y)

    def draw_polygon(self, vertices):
        if self.polygon_item is not None:
            # Entferne das alte Polygon-Item von der Szene, falls vorhanden
            self.scene.removeItem(self.polygon_item)

        if vertices:
            polygon = QPolygonF(vertices)
            pen = QPen(QColor(Qt.red))
            self.polygon_item = self.scene.addPolygon(polygon, pen)

    def draw_agent(self, agent):
        if agent is not None:
            if self.agent_item is not None:
                # Entferne das alte Agent-Item von der Szene, falls vorhanden
                self.scene.removeItem(self.agent_item)

            agent_rect = QGraphicsRectItem(agent.position.x(), agent.position.y(), 
                                           agent.width, agent.height)
            agent_rect.setPen(QPen(QColor(Qt.blue)))
            self.agent_item = self.scene.addItem(agent_rect)