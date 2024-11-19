# file_handler.py
from tkinter import filedialog
from editor import Editor


class FileHandler:
    def __init__(self, editor: Editor):
        self.editor = editor

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("XML/JSON файлы", "*.xml *.json"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return None
        try:
            if filepath.endswith(".xml"):
                self.editor.load_xml(filepath)
            elif filepath.endswith(".json"):
                self.editor.load_json(filepath)
            return filepath
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return None

    def save_file(self, filepath):
        try:
            if self.editor.file_type == "XML":
                self.editor.save_xml(filepath)
            elif self.editor.file_type == "JSON":
                self.editor.save_json(filepath)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
