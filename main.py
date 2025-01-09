# main.py
from model import DataModel
from view import View
from controller import Controller


def main():
    model = DataModel()
    view = View()
    controller = Controller(model, view)
    view.mainloop()


if __name__ == "__main__":
    main()
