# main.py
from tkinter import Tk
from ui import EditorUI

if __name__ == "__main__":
    root = Tk()
    app = EditorUI(root)
    root.geometry("1000x700")
    root.mainloop()
