from model import CoverageModel
from view import CoverageView
from controller import CoverageController


def main():
    model = CoverageModel()
    view = CoverageView(model)
    controller = CoverageController(model, view)
    view.show()
    controller.run()


if __name__ == "__main__":
    main()
