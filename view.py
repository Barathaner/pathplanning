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
    QGraphicsPolygonItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsEllipseItem,
    QWidget,
    QLineEdit,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QPointF, QTimer, QCoreApplication
from PyQt5.QtGui import QPolygonF, QPen, QColor, QIntValidator, QBrush
from shapely.geometry import Point


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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_agent_position)
        self.agent_speed = 1  # Geschwindigkeit des Agenten (kann angepasst werden)

        self.agent_item = None
        self.polygon_item = None
        self.grid_items = []
        self.pathitem = None

        # Raster- und Canvas-Größen
        self.raster_size = 32
        self.canvas_size = 1000
        self.cell_size = self.canvas_size / self.raster_size

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.canvas_size, self.canvas_size)
        self.view = QGraphicsView(self.scene, self)

        # Create the buttons
        self.start_button = QPushButton("Draw Grid", self)
        self.restart_button = QPushButton("Restart", self)
        self.AgentInfos_button = QPushButton("AgentInfos", self)
        self.start_agent_button = QPushButton("Start Agent", self)
        self.stop_agent_button = QPushButton("Stop Agent", self)
        self.end_button = QPushButton("End", self)

        # Create a QHBoxLayout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.AgentInfos_button)
        button_layout.addWidget(self.start_agent_button)
        button_layout.addWidget(self.stop_agent_button)
        button_layout.addWidget(self.end_button)

        self.start_agent_button.clicked.connect(self.start_agent_animation)
        self.stop_agent_button.clicked.connect(self.stop_agent_animation)
        self.end_button.clicked.connect(QCoreApplication.instance().quit)
        self.AgentInfos_button.clicked.connect(self.openNumbersDialog)
        self.start_button.clicked.connect(self.startGrid)
        self.restart_button.clicked.connect(controller.reset_grid)

        # Create a QVBoxLayout
        layout = QVBoxLayout()

        # Add the QHBoxLayout and QGraphicsView to the QVBoxLayout
        layout.addLayout(button_layout)
        layout.addWidget(self.view)

        # Create a QWidget, set its layout, and set it as the central widget of the QMainWindow
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setWindowTitle("Polygon Drawer")
        self.setGeometry(100, 100, self.canvas_size + 100, self.canvas_size + 100)

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.mousePressEvent

        self.draw_grid()

    def startGrid(self):
        self.controller.handle_enter_pressed()

    def draw_grid(self):
        for i in range(self.raster_size + 1):
            # Vertikale Linien
            self.scene.addLine(
                i * self.cell_size,
                0,
                i * self.cell_size,
                self.canvas_size,
                QPen(QColor(220, 220, 220)),
            )
            # Horizontale Linien
            self.scene.addLine(
                0,
                i * self.cell_size,
                self.canvas_size,
                i * self.cell_size,
                QPen(QColor(220, 220, 220)),
            )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_X:
            self.openNumbersDialog()

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.controller.handle_enter_pressed()

    def draw_path(self, path):
        # Entfernen Sie zuerst alle alten Linien, Punkte und Labels, wenn sie existieren
        if self.pathitem:
            for item in self.pathitem:
                self.scene.removeItem(item)
            self.pathitem.clear()

        # Initialisieren Sie self.pathitem als Liste, wenn sie noch nicht existiert
        if self.pathitem is None:
            self.pathitem = []

        # Zeichnen Sie den neuen Pfad
        if path:
            for i in range(len(path)):
                # Zeichnen der Linie zwischen den Punkten
                if i < len(path) - 1:
                    line = QGraphicsLineItem(
                        path[i].x * self.cell_size,
                        path[i].y * self.cell_size,
                        path[i + 1].x * self.cell_size,
                        path[i + 1].y * self.cell_size,
                    )
                    line.setPen(QPen(QColor(Qt.green), 2))
                    self.scene.addItem(line)
                    self.pathitem.append(line)

                # Zeichnen des Punktes
                point_size = 5  # Die Größe des Punktes, kann angepasst werden
                point = QGraphicsEllipseItem(
                    path[i].x * self.cell_size - point_size / 2,
                    path[i].y * self.cell_size - point_size / 2,
                    point_size,
                    point_size,
                )
                point.setBrush(QBrush(QColor(Qt.red)))
                self.scene.addItem(point)
                self.pathitem.append(point)

                # Hinzufügen des Labels
                label = QGraphicsTextItem(str(i))
                label.setPos(path[i].x * self.cell_size, path[i].y * self.cell_size)
                self.scene.addItem(label)
                self.pathitem.append(label)
                print("Pfad:", i, path[i].x, path[i].y)

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
            x = vertex.x * self.cell_size
            y = vertex.y * self.cell_size
            self.scene.addRect(
                x,
                y,
                self.cell_size,
                self.cell_size,
                QPen(Qt.NoPen),
                QBrush(QColor(Qt.black)),
            )

    def draw_polygons(self, polygons):
        # Entferne zuerst alle alten Polygone, wenn sie existieren
        if len(self.grid_items) > 0:
            for item in self.grid_items:
                self.scene.removeItem(item)
            self.grid_items.clear()

        # Zeichne die neuen Polygone
        for polygon in polygons:
            qpoly = QPolygonF()
            for point in polygon.exterior.coords:
                qpoly.append(
                    QPointF(point[0] * self.cell_size, point[1] * self.cell_size)
                )

            polygon_item = QGraphicsPolygonItem(qpoly)
            polygon_item.setPen(QPen(QColor(Qt.blue), 2))
            polygon_item.setBrush(QBrush(QColor(0, 0, 255, 100)))
            self.scene.addItem(polygon_item)
            self.grid_items.append(polygon_item)  # Füge das Item zur Liste hinzu

    def draw_polygon(self, vertices):
        if self.polygon_item is not None:
            self.scene.removeItem(self.polygon_item)

        if vertices:
            pixel_vertices = [
                QPointF(v.x * self.cell_size, v.y * self.cell_size) for v in vertices
            ]
            polygon = QPolygonF(pixel_vertices)
            pen = QPen(QColor(Qt.red))
            self.polygon_item = self.scene.addPolygon(polygon, pen)
            self.draw_polygon_vertices(vertices)

    def draw_agent(self, agent):
        print("Agent:", agent)
        if agent is not None:
            if self.agent_item is not None:
                self.scene.removeItem(self.agent_item)

            agent_x = agent.position.x * self.cell_size
            agent_y = agent.position.y * self.cell_size
            agent_width = agent.width * self.cell_size
            agent_height = agent.height * self.cell_size

            agent_rect = QGraphicsRectItem(agent_x, agent_y, agent_width, agent_height)
            agent_rect.setPen(QPen(QColor(Qt.blue)))
            agent_rect.setBrush(QBrush(QColor(Qt.blue)))
            self.agent_item = self.scene.addItem(agent_rect)

    def update_agent_position(self):
        print("Update Agent Position")

        if self.controller.model.agent:
            print(self.controller.model.agent)
            # Holen Sie die aktuellen Koordinaten des Agenten
            current_x = self.controller.model.agent.position.x
            current_y = self.controller.model.agent.position.y
            current_width = self.controller.model.agent.width
            current_height = self.controller.model.agent.height

            # Entferne den aktuellen Agenten
            self.controller.remove_agent()

            # Berechne die neuen Koordinaten des Agenten
            new_x = current_x + 1
            new_y = current_y + 1

            # Erstelle einen neuen Agenten an den neuen Koordinaten
            self.controller.create_agent(current_width, current_height, new_x, new_y)

    def start_agent_animation(self):
        self.timer.start(500)

    def stop_agent_animation(self):
        self.timer.stop()


class WelcomeView(QWidget):
    def __init__(self, start_callback, controller):
        super().__init__()

        self.controller = controller
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
        start_button.setObjectName("StartButton")

        self.setLayout(self.layout)

        # Setze die gewünschte Größe für das Welcome-Fenster
        self.resize(1200, 600)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Rufe die click-Methode des Start-Buttons auf
            start_button = self.findChild(QPushButton, "StartButton")
            if start_button:
                start_button.click()

    def close_welcome_view(self):
        self.close()
        inputs = [lineEdit.text() for lineEdit in self.lineEdits]

        # Überprüfe, ob alle Eingabefelder Werte enthalten
        if all(inputs):
            try:
                # Versuche die eingegebenen Werte in Ganzzahlen umzuwandeln
                inputs_as_int = [int(value) for value in inputs]
                # Rufe die create_agent-Methode des Controllers auf
                print("Eingegebene Werte:", inputs_as_int)
                # self.controller.create_agent(*inputs_as_int)
                self.close()  # Schließe das Welcome-Fenster
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter valid integers.")
