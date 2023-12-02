import sys
from PyQt5.QtWidgets import QApplication
from model import Model
from model import WelcomeModel
from view import PolygonView, WelcomeView
from controller import PolygonController
from controller import WelcomeController


def main():
    app = QApplication(sys.argv)

    def show_polygon_view():
        welcome_view.close_welcome_view()  # Schließe den Welcome Screen
        model = Model()
        controller = PolygonController(model, None)
        view = PolygonView(controller)
        controller.view = view
        view.show()

    welcome_model = WelcomeModel()
    welcome_controller = WelcomeController(welcome_model, None)
    welcome_view = WelcomeView(show_polygon_view, welcome_controller)
    welcome_controller.view = welcome_view
    welcome_view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
