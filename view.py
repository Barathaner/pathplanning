from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPolygonF, QPen, QColor

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class NumbersInputDialog(QDialog):
    def __init__(self, parent=None):
        super(NumbersInputDialog, self).__init__(parent)

        self.setWindowTitle("Agent-Infos")

        self.layout = QVBoxLayout(self)

        # Labels und LineEdits für die Eingaben
        input_labels = ["Width:", "Height:", "X-Position:", "Y-Position:"]
        self.lineEdits = []

        for label_text in input_labels:
            self.layout.addWidget(QLabel(label_text))
            lineEdit = QLineEdit(self)
            self.lineEdits.append(lineEdit)
            self.layout.addWidget(lineEdit)

        # OK und Cancel Buttons
        self.buttons = QPushButton("OK", self)
        self.buttons.clicked.connect(self.accept)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)

    def getInputs(self):
        return [lineEdit.text() for lineEdit in self.lineEdits]


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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.openNumbersDialog()

    def openNumbersDialog(self):
        dialog = NumbersInputDialog(self)
        if dialog.exec_():
            numbers = dialog.getNumbers()
            print(numbers)  # Hier können Sie etwas mit den Zahlen machen

    def mousePressEvent(self, event):
        scenePos = self.view.mapToScene(event.pos())

        x = scenePos.x()
        y = scenePos.y()
        self.controller.add_vertex(x, y)

    def draw_polygon(self, vertices):
        self.scene.clear()

        if vertices:
            polygon = QPolygonF(vertices)

            pen = QPen(QColor(Qt.red))
            self.scene.addPolygon(polygon, pen)
