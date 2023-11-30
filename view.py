from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGraphicsLineItem,
    
    QWidget,
    QLineEdit,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPolygonF, QPen, QColor, QIntValidator,QBrush


class AgentInputDialog(QDialog):
    def __init__(self, parent=None):
        super(AgentInputDialog, self).__init__(parent)

        self.setWindowTitle("Agent-infos")

        self.layout = QVBoxLayout(self)

        # Labels und LineEdits für die Eingaben
        input_labels = ["Width:", "Height:", "X-Position:", "Y-Position:"]
        self.lineEdits = []

        for label_text in input_labels:
            self.layout.addWidget(QLabel(label_text))
            lineEdit = QLineEdit(self)

            # Eingabe auf ganze Zahlen beschränken
            lineEdit.setValidator(QIntValidator())

            self.lineEdits.append(lineEdit)
            self.layout.addWidget(lineEdit)

        # OK und Cancel Buttons
        self.buttons = QPushButton("OK", self)
        self.buttons.clicked.connect(
            self.on_ok_clicked
        )  # Verbinde mit benutzerdefinierter Methode
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)

    def on_ok_clicked(self):
        inputs = self.getValues()

        # Überprüfe, ob alle Eingabefelder Werte enthalten
        if all(inputs):
            try:
                inputs_as_int = [int(value) for value in inputs]
                self.accept()  # Schließe das Dialogfenster
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter valid integers.")
        else:
            QMessageBox.warning(self, "Error", "Please fill in all input fields.")

    def getValues(self):
        return [lineEdit.text() for lineEdit in self.lineEdits]


class PolygonView(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.agent_item = None
        self.polygon_item = None

        # Raster- und Canvas-Größen
        self.raster_size = 50
        self.canvas_size = 1000
        self.cell_size = self.canvas_size / self.raster_size

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.canvas_size, self.canvas_size)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.setWindowTitle("Polygon Drawer")
        self.setGeometry(100, 100, self.canvas_size + 100, self.canvas_size + 100)

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.mousePressEvent

        self.draw_grid()    


    def draw_grid(self):
        for i in range(self.raster_size + 1):
            # Vertikale Linien
            self.scene.addLine(i * self.cell_size, 0, i * self.cell_size, self.canvas_size, QPen(QColor(220, 220, 220)))
            # Horizontale Linien
            self.scene.addLine(0, i * self.cell_size, self.canvas_size, i * self.cell_size, QPen(QColor(220, 220, 220)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.openNumbersDialog()

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.controller.handle_enter_pressed()

    def draw_path(self, path):
        if path:
            for i in range(len(path) - 1):
                line = QGraphicsLineItem(
                    path[i].x()* self.cell_size, path[i].y()* self.cell_size, path[i + 1].x()* self.cell_size, path[i + 1].y()* self.cell_size
                )
                line.setPen(QPen(QColor(Qt.green), 2))
                self.scene.addItem(line)


    def openNumbersDialog(self):
        dialog = AgentInputDialog(self)
        if dialog.exec_():
            values = dialog.getValues()
            if len(values) == 4:
                width, height, x, y = map(int, values)
                print("Eingegebene Werte:", width, height, x, y)
                self.controller.create_agent(width, height, x, y)

    def mousePressEvent(self, event):
        scenePos = self.view.mapToScene(event.pos())
        raster_x = int(scenePos.x() / self.cell_size)
        raster_y = int(scenePos.y() / self.cell_size)
        self.controller.add_vertex(raster_x, raster_y)

    def draw_polygon_vertices(self, vertices):
            for vertex in vertices:
                x = vertex.x() * self.cell_size
                y = vertex.y() * self.cell_size
                self.scene.addRect(x, y, self.cell_size, self.cell_size, QPen(Qt.NoPen), QBrush(QColor(Qt.black)))

    def draw_polygon(self, vertices):
        if self.polygon_item is not None:
            self.scene.removeItem(self.polygon_item)

        if vertices:
            pixel_vertices = [QPointF(v.x() * self.cell_size, v.y() * self.cell_size) for v in vertices]
            polygon = QPolygonF(pixel_vertices)
            pen = QPen(QColor(Qt.red))
            self.polygon_item = self.scene.addPolygon(polygon, pen)
            self.draw_polygon_vertices(vertices)

    def draw_agent(self, agent):
        if agent is not None:
            if self.agent_item is not None:
                self.scene.removeItem(self.agent_item)

            agent_x = agent.position.x() * self.cell_size
            agent_y = agent.position.y() * self.cell_size
            agent_width = agent.width * self.cell_size
            agent_height = agent.height * self.cell_size

            agent_rect = QGraphicsRectItem(agent_x, agent_y, agent_width, agent_height)
            agent_rect.setPen(QPen(QColor(Qt.blue)))
            agent_rect.setBrush(QBrush(QColor(Qt.blue)))
            self.agent_item = self.scene.addItem(agent_rect)


class WelcomeView(QWidget):
    def __init__(self, start_callback, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        label = QLabel("Welcome to the Pathplanner!")
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.addWidget(label)

        # Erstelle ein horizontales Layout für die linke und rechte Seite
        horizontal_layout = QHBoxLayout()

        # Linke Seite
        left_widget = QWidget()
        left_widget.setFixedWidth(500)  # Setze die gewünschte Breite
        left_layout = QVBoxLayout(left_widget)
        agent_inputs_label = QLabel("Agent-Inputs")
        agent_inputs_label.setAlignment(Qt.AlignHCenter)
        left_layout.addWidget(agent_inputs_label)

        # Füge vier Inputs hinzu
        input_labels = ["Width:", "Height:", "X-Position:", "Y-Position:"]
        self.lineEdits = []

        for label_text in input_labels:
            left_layout.addWidget(QLabel(label_text))
            lineEdit = QLineEdit(left_widget)
            # Eingabe auf ganze Zahlen beschränken
            lineEdit.setValidator(QIntValidator())
            self.lineEdits.append(lineEdit)
            left_layout.addWidget(lineEdit)

        # Rechte Seite
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        control_label = QLabel("Controls")
        control_label.setAlignment(Qt.AlignHCenter)
        right_layout.addWidget(control_label)
        right_widget.setFixedWidth(500)  # Setze die gewünschte Breite

        # Füge Erklärungen für die Steuerung hinzu
        control_layouts = [
            "Draw Polygon with Mouse",
            "Click X to change the Agent-Infos",
            "Click Enter to start the Pathplanning",
        ]

        for control_text in control_layouts:
            right_layout.addWidget(QLabel(control_text))

        # Füge die linken und rechten Widgets zum horizontalen Layout hinzu
        horizontal_layout.addWidget(left_widget)
        horizontal_layout.addWidget(right_widget)

        # Füge das horizontale Layout zum Hauptlayout hinzu
        self.layout.addLayout(horizontal_layout)

        start_button = QPushButton("Start")
        start_button.clicked.connect(start_callback)
        start_button.setFocusPolicy(Qt.StrongFocus)
        self.layout.addWidget(start_button)

        self.setLayout(self.layout)

        # Setze die gewünschte Größe für das Welcome-Fenster
        self.resize(1200, 600)

    def close_welcome_view(self):
        self.close()
        # inputs = [lineEdit.text() for lineEdit in self.lineEdits]

        # # Überprüfe, ob alle Eingabefelder Werte enthalten
        # if all(inputs):
        #     try:
        #         # Versuche die eingegebenen Werte in Ganzzahlen umzuwandeln
        #         inputs_as_int = [int(value) for value in inputs]
        #         # Rufe die create_agent-Methode des Controllers auf
        #         print("Eingegebene Werte:", inputs_as_int)
        #         self.controller.create_agent(*inputs_as_int)
        #         self.close()  # Schließe das Welcome-Fenster
        #     except ValueError:
        #         QMessageBox.warning(self, "Error", "Please enter valid integers.")
        # else:
        #     QMessageBox.warning(self, "Error", "Please fill in all input fields.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.layout.itemAt(
                2
            ).widget().click()  # Simuliere einen Klick auf den Start-Button
        else:
            super().keyPressEvent(event)
