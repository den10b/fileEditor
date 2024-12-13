# # main.py
# import json
# from tkinter import Tk
# from ui import EditorUI
#
# if __name__ == "__main__":
#     # jsondata=json.load("test_json.json")
#     # print(jsondata)
#     root = Tk()
#     app = EditorUI(root)
#     root.geometry("1000x700")
#     root.mainloop()

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