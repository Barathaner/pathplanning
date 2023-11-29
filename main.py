from model import CoverageModel
from view import CoverageView
from controller import CoverageController


def main():
    model = CoverageModel()
    view = CoverageView(model)
    controller = CoverageController(model, view)
    controller.run()
    view.show()


if __name__ == "__main__":
    main()
