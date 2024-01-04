# main.py
import sys
from PyQt5.QtWidgets import QApplication
from Models.model import Model
from view import PolygonView, WelcomeView
from controller import PolygonController


def main():
    app = QApplication(sys.argv)
    model = Model()
    polygon_controller = PolygonController(model, None)

    # Create the WelcomeView with the PolygonController
    welcome_view = WelcomeView(
        polygon_controller.handle_enter_pressed, polygon_controller
    )

    # Set the view of the controller to the WelcomeView
    polygon_controller.view = welcome_view

    welcome_view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
