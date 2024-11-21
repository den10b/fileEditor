# file_handler.py
from tkinter import filedialog
from editor import XMLEditor, JSONEditor


class FileHandler:
    def __init__(self):
        self.editor = None
        self.file_type = None

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("XML/JSON файлы", "*.xml *.json"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return None

        if filepath.endswith(".xml"):
            self.editor = XMLEditor()
            self.file_type = "XML"
        elif filepath.endswith(".json"):
            self.editor = JSONEditor()
            self.file_type = "JSON"
        else:
            # Можно добавить обработку других типов или показать ошибку
            return None

        try:
            self.editor.load(filepath)
            return filepath
        except Exception as e:
            # Логирование ошибки или показ пользователю
            print(f"Ошибка при загрузке файла: {e}")
            return None

    def save_file(self, filepath):
        if not self.editor:
            return

        try:
            self.editor.save(filepath)
        except Exception as e:
            # Логирование ошибки или показ пользователю
            print(f"Ошибка при сохранении файла: {e}")
