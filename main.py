import sys
from PyQt5.QtWidgets import QApplication
from Models.model import Model
from view import PolygonView, WelcomeView
from controller import PolygonController
from controller import WelcomeController


def main():
    app = QApplication(sys.argv)
    model = Model()
    controller = PolygonController(model, None)
    view = PolygonView(controller)
    controller.view = view
    view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
