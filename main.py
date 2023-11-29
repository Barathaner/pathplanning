import sys
from PyQt5.QtWidgets import QApplication
from model import PolygonModel
from view import PolygonView
from controller import PolygonController

def main():
    app = QApplication(sys.argv)
    model = PolygonModel()
    controller = PolygonController(model, None)
    view = PolygonView(controller)
    controller.view = view
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
