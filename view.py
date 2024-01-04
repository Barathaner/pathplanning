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
    QCheckBox,
    QGraphicsPixmapItem,
)
from PyQt5.QtCore import Qt, QPointF, QTimer, QCoreApplication, QRectF
from PyQt5.QtGui import *
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

            # Setze den Standardwert auf 2
            lineEdit.setText("2")

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


class ExplanationDialog(QDialog):
    def __init__(self, parent=None):
        super(ExplanationDialog, self).__init__(parent)

        self.setWindowTitle("Explanation")

        layout = QVBoxLayout(self)

        explanation_label = QLabel(
            "Hier kommt dein Erklärungstext.\n"
            "Du kannst diesen Text nach deinen Bedürfnissen anpassen."
        )
        layout.addWidget(explanation_label)

        self.setLayout(layout)


class PolygonView(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.tractor_item = None  # Fügen Sie diese Zeile hinzu

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
        self.help_button = QPushButton("?", self)

        # Create a QHBoxLayout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.AgentInfos_button)
        button_layout.addWidget(self.start_agent_button)
        button_layout.addWidget(self.stop_agent_button)
        button_layout.addWidget(self.end_button)
        button_layout.addWidget(self.help_button)

        self.start_agent_button.clicked.connect(self.start_agent_animation)
        self.stop_agent_button.clicked.connect(self.stop_agent_animation)
        self.end_button.clicked.connect(QCoreApplication.instance().quit)
        self.AgentInfos_button.clicked.connect(self.openNumbersDialog)
        self.start_button.clicked.connect(self.startGrid)
        self.restart_button.clicked.connect(controller.reset_grid)
        self.help_button.clicked.connect(self.show_explanation_dialog)

        # Create the checkboxes
        self.show_agent_path_checkbox = QCheckBox("Show agent_path", self)
        self.show_coverage_path_checkbox = QCheckBox("Show coverage_path", self)
        self.show_polygons_checkbox = QCheckBox("Show polygons", self)
        self.show_grid_checkbox = QCheckBox("Show grid", self)
        self.show_background_checkbox = QCheckBox(
            "Show background", self
        )  # Add this line

        # Set the default state for the checkboxes
        self.show_agent_path_checkbox.setChecked(True)
        self.show_coverage_path_checkbox.setChecked(False)
        self.show_polygons_checkbox.setChecked(True)
        self.show_grid_checkbox.setChecked(False)  # Default to showing the grid
        self.show_background_checkbox.setChecked(
            True
        )  # Default to showing the background image

        # Configure checkbox mutual exclusion
        self.show_agent_path_checkbox.toggled.connect(self.update_checkboxes)
        self.show_coverage_path_checkbox.toggled.connect(self.update_checkboxes)
        self.show_polygons_checkbox.stateChanged.connect(self.update_checkboxes)
        self.show_grid_checkbox.stateChanged.connect(self.update_checkboxes)
        self.show_background_checkbox.stateChanged.connect(
            self.update_checkboxes
        )  # Add this line

        # Create a QHBoxLayout for the checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.show_agent_path_checkbox)
        checkbox_layout.addWidget(self.show_coverage_path_checkbox)
        checkbox_layout.addWidget(self.show_polygons_checkbox)
        checkbox_layout.addWidget(self.show_grid_checkbox)
        checkbox_layout.addWidget(self.show_background_checkbox)  # Add this line

        # Create a QVBoxLayout for buttons and checkboxes
        main_layout = QVBoxLayout()

        # Add the QHBoxLayout with buttons to the QVBoxLayout
        main_layout.addLayout(button_layout)

        # Add the QHBoxLayout with checkboxes to the QVBoxLayout
        main_layout.addLayout(checkbox_layout)

        # Add the QGraphicsView to the QVBoxLayout
        main_layout.addWidget(self.view)

        # Create a QWidget, set its layout, and set it as the central widget of the QMainWindow
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.setWindowTitle("Polygon Drawer")
        self.setGeometry(100, 100, self.canvas_size + 100, self.canvas_size + 100)

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.mousePressEvent

        # Check if the "Show grid" checkbox is checked
        # if self.show_grid_checkbox.isChecked():
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

        self.draw_grid()

    def startGrid(self):
        self.controller.handle_enter_pressed()

    def draw_grid(self):
        # Verstecke alle Linien
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                if self.show_grid_checkbox.isChecked():
                    item.show()
                else:
                    item.hide()

        # Check if the "Show background" checkbox is checked
        if self.show_background_checkbox.isChecked():
            # Set the background image
            background_image = (
                "farmImage.jpg"  # Replace with the actual path to your image
            )
        else:
            background_image = None

        pixmap = QPixmap(self.canvas_size, self.canvas_size)
        pixmap.fill(
            Qt.transparent
        )  # Fill with transparency, change to the desired background color if needed
        painter = QPainter(pixmap)
        painter.drawPixmap(
            0, 0, self.canvas_size, self.canvas_size, QPixmap(background_image)
        )
        painter.end()
        background_brush = QBrush(pixmap)
        self.view.setBackgroundBrush(background_brush)

    def draw_tractor(self, agent):
        # Lade das Traktor-Bild
        tractor_pixmap = QPixmap("tractor.jpg")

        if tractor_pixmap.isNull():
            print("Error loading tractor image")
            return

        # Berechne die skalierten Abmessungen
        scaled_width = agent.width * self.cell_size
        scaled_height = agent.height * self.cell_size

        # Skaliere das Bild mit einer Transformation
        transform = QTransform().scale(
            scaled_width / tractor_pixmap.width(),
            scaled_height / tractor_pixmap.height(),
        )
        scaled_pixmap = tractor_pixmap.transformed(transform, Qt.SmoothTransformation)

        # Erstelle ein QGraphicsPixmapItem mit dem skalierten QPixmap
        tractor_item = QGraphicsPixmapItem(scaled_pixmap)

        # Füge das QGraphicsPixmapItem zur Szene hinzu
        self.scene.addItem(tractor_item)

        # Positioniere das QGraphicsPixmapItem entsprechend den Agenteninformationen
        tractor_item.setPos(
            agent.position.x * self.cell_size, agent.position.y * self.cell_size
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

    def update_checkboxes(self):
        sender_checkbox = self.sender()

        if (
            sender_checkbox == self.show_agent_path_checkbox
            and self.show_agent_path_checkbox.isChecked()
        ):
            # Wenn show_agent_path_checkbox aktiviert ist, deaktiviere show_coverage_path_checkbox
            self.show_coverage_path_checkbox.setChecked(False)
        elif (
            sender_checkbox == self.show_coverage_path_checkbox
            and self.show_coverage_path_checkbox.isChecked()
        ):
            # Wenn show_coverage_path_checkbox aktiviert ist, deaktiviere show_agent_path_checkbox
            self.show_agent_path_checkbox.setChecked(False)

        # Rufe die draw_grid-Funktion auf, um das Gitter neu zu zeichnen
        self.startGrid()

        # Rufe die draw_grid-Funktion auf, um das Gitter neu zu zeichnen
        self.draw_grid()

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

    def show_explanation_dialog(self):
        explanation_dialog = ExplanationDialog(self)
        explanation_dialog.exec_()

    def draw_polygons(self, polygons):
        # Entferne zuerst alle alten Polygone, wenn sie existieren
        if len(self.grid_items) > 0:
            for item in self.grid_items:
                self.scene.removeItem(item)
            self.grid_items.clear()

        # Zeichne die neuen Polygone, wenn die Checkbox aktiviert ist
        if self.show_polygons_checkbox.isChecked():
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

        # Rufe die draw_grid-Funktion auf, um das Gitter neu zu zeichnen
        self.draw_grid()

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
        if agent is not None:
            # Entferne den alten Agenten, falls vorhanden
            if self.agent_item is not None:
                self.scene.removeItem(self.agent_item)

            agent_x = agent.position.x * self.cell_size
            agent_y = agent.position.y * self.cell_size
            agent_width = agent.width * self.cell_size
            agent_height = agent.height * self.cell_size

            # Zeichne den neuen Agenten
            polyvertices = []
            polyvertices.append(QPointF(agent_x, agent_y))
            polyvertices.append(QPointF(agent_x + agent_width, agent_y))
            polyvertices.append(QPointF(agent_x + agent_width, agent_y + agent_height))
            polyvertices.append(QPointF(agent_x, agent_y + agent_height))

            qpoly = QPolygonF(polyvertices)
            polygon_item = QGraphicsPolygonItem(qpoly)
            polygon_item.setPen(QPen(QColor(Qt.green), 2))
            polygon_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
            self.scene.addItem(polygon_item)
            self.agent_item = polygon_item  # Aktualisiere self.agent_item

        # Zeichne den Traktor
        # self.draw_tractor(agent)

    def update_agent_position(self):
        print("Update Agent Position")

        if not self.controller.model.agent_path:
            print("Agent Path is empty, stopping animation.")
            self.timer.stop()
            return

        # Holen Sie die aktuellen Koordinaten des Agenten aus dem Pfad
        current_position = self.controller.model.agent_path.pop(0)
        current_x, current_y = current_position.x, current_position.y

        # Entfernen Sie den aktuellen Agenten aus der Szene
        if self.agent_item is not None:
            self.scene.removeItem(self.agent_item)

        # Erstelle einen neuen Agenten an den neuen Koordinaten
        self.controller.create_agent(
            self.controller.model.agent.width,
            self.controller.model.agent.height,
            current_x,
            current_y,
        )

        # Entferne auch das vorherige Traktor-Bild
        if self.tractor_item is not None:
            self.scene.removeItem(self.tractor_item)

        # Zeichnen Sie das neue Traktor-Bild in der Szene
        # self.draw_tractor(self.controller.model.agent)

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
            # Set the default value
            lineEdit.setText("2")
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

    def start_pathplanning(self):
        # Extrahiere die Werte aus den LineEdits
        agent_width_text = self.lineEdits[0].text()
        agent_height_text = self.lineEdits[1].text()
        agent_x_text = self.lineEdits[2].text()
        agent_y_text = self.lineEdits[3].text()

        # Überprüfe, ob alle Eingaben vorhanden sind
        if all([agent_width_text, agent_height_text, agent_x_text, agent_y_text]):
            # Wenn alle Eingaben vorhanden sind, konvertiere sie in Ganzzahlen
            agent_width = int(agent_width_text)
            agent_height = int(agent_height_text)
            agent_x = int(agent_x_text)
            agent_y = int(agent_y_text)

            self.controller.start_pathplanning(
                agent_width, agent_height, agent_x, agent_y
            )
        else:
            self.controller.start_pathplanning(0, 0, 0, 0)

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
    #         # Rufe die click-Methode des Start-Buttons auf
    #         start_button = self.findChild(QPushButton, "StartButton")
    #         if start_button:
    #             start_button.click()

    # def close_welcome_view(self):
    #     self.close()
    #     inputs = [lineEdit.text() for lineEdit in self.lineEdits]

    #     # Überprüfe, ob alle Eingabefelder Werte enthalten
    #     if all(inputs):
    #         try:
    #             # Versuche die eingegebenen Werte in Ganzzahlen umzuwandeln
    #             inputs_as_int = [int(value) for value in inputs]
    #             # Rufe die create_agent-Methode des Controllers auf
    #             print("Eingegebene Werte:", inputs_as_int)
    #             # self.controller.create_agent(*inputs_as_int)
    #             self.close()  # Schließe das Welcome-Fenster
    #         except ValueError:
    #             QMessageBox.warning(self, "Error", "Please enter valid integers.")
