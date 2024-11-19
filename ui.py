# ui.py
from tkinter import Frame, Menu, PanedWindow, messagebox, simpledialog, ttk, filedialog
from file_handler import FileHandler
from editor import Editor
from utils import get_expanded_nodes, set_expanded_nodes
import xml.etree.ElementTree as ET
import json

class EditorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML/JSON Editor")

        # Инициализация редактора данных и обработчика файлов
        self.editor = Editor()
        self.file_handler = FileHandler(self.editor)

        # Панель инструментов
        self.create_toolbar(root)

        # Основное окно
        self.main_frame = PanedWindow(root, orient="horizontal")
        self.main_frame.pack(fill="both", expand=True)

        # Древовидная структура
        self.tree_frame = Frame(self.main_frame)
        self.tree = ttk.Treeview(self.tree_frame, columns=("Value",), show="tree headings")
        self.tree.heading("#0", text="Node")
        self.tree.heading("Value", text="Value")
        self.tree.column("#0", anchor="w", width=200, stretch=True)
        self.tree.column("Value", anchor="w", width=300, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewClose>>", self.on_tree_close)
        self.main_frame.add(self.tree_frame)

        # Стиль для атрибутов
        style = ttk.Style()
        style.configure("Treeview.tag.Attribute", foreground="blue")
        self.tree.tag_configure("attribute", foreground="blue")

        # Меню
        self.create_menu(root)

    def create_toolbar(self, root):
        toolbar = Frame(root, bd=1, relief="raised")
        ttk.Button(toolbar, text="Добавить узел", command=self.add_node).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Удалить узел", command=self.delete_node).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Редактировать узел", command=self.edit_node).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Сохранить", command=self.save_file).pack(side="left", padx=2, pady=2)
        toolbar.pack(side="top", fill="x")

    def create_menu(self, root):
        menubar = Menu(root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menubar)

    def open_file(self):
        filepath = self.file_handler.open_file()
        if filepath:
            self.refresh_ui()
        else:
            messagebox.showerror("Ошибка", "Не удалось открыть файл.")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension="",
            filetypes=[("XML/JSON файлы", "*.xml *.json"), ("Все файлы", "*.*")]
        )
        if filepath:
            self.file_handler.save_file(filepath)

    def add_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для добавления.")
            return

        new_node_name = simpledialog.askstring("Добавить узел", "Введите имя нового узла:")
        if new_node_name is None:  # Отмена
            return

        parent_path = self.get_tree_path(selected_item)
        parent_data = self.get_data_from_path(parent_path)

        if self.editor.file_type == "JSON":
            if isinstance(parent_data, dict):
                parent_data[new_node_name] = None
            elif isinstance(parent_data, list):
                parent_data.append({new_node_name: None})
        elif self.editor.file_type == "XML":
            parent_element = parent_data
            self.editor.add_node(parent_element, new_node_name)

        self.refresh_ui()

    def delete_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для удаления.")
            return

        parent_item = self.tree.parent(selected_item)
        parent_path = self.get_tree_path(parent_item)
        parent_data = self.get_data_from_path(parent_path)

        current_node = self.tree.item(selected_item, "text")

        if self.editor.file_type == "JSON":
            if isinstance(parent_data, dict):
                parent_data.pop(current_node, None)
            elif isinstance(parent_data, list):
                try:
                    index = int(current_node.strip("[]"))
                    parent_data.pop(index)
                except (ValueError, IndexError):
                    messagebox.showerror("Ошибка", "Неверный индекс элемента.")
                    return
        elif self.editor.file_type == "XML":
            child_element = self.get_xml_element_by_path(selected_item)
            if child_element is not None:
                self.editor.delete_node(parent_data, child_element)

        self.refresh_ui()

    def edit_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для редактирования.")
            return

        current_value = self.tree.item(selected_item, "text")
        current_column = self.tree.item(selected_item, "values")[0] if self.tree.item(selected_item, "values") else ""

        # Спрашиваем новое значение
        new_value = simpledialog.askstring("Редактировать", f"Введите новое значение для {current_value}:",
                                           initialvalue=current_column)
        if new_value is None:  # Отмена
            return

        if self.editor.file_type == "JSON":
            current_path = self.get_tree_path(selected_item)
            parent_path = current_path[:-1]
            key = current_path[-1]
            parent_data = self.get_data_from_path(parent_path)

            if isinstance(parent_data, dict):
                parent_data[key] = new_value
            elif isinstance(parent_data, list):
                try:
                    index = int(key.strip("[]"))
                    parent_data[index] = new_value
                except (ValueError, IndexError):
                    messagebox.showerror("Ошибка", "Неверный индекс элемента.")
                    return
        elif self.editor.file_type == "XML":
            element = self.get_xml_element_by_path(selected_item)
            if element is not None:
                element.text = new_value

        self.refresh_ui()

    def refresh_ui(self):
        tree_state = get_expanded_nodes(self.tree)
        self.tree.delete(*self.tree.get_children())
        if self.editor.file_type == "XML":
            self.display_xml(self.editor.data)
        elif self.editor.file_type == "JSON":
            self.display_json(self.editor.data)
        set_expanded_nodes(self.tree, tree_state)

    def display_xml(self, element, parent=""):
        node_id = self.tree.insert(parent, "end", text=element.tag, values=(""))

        # Если у узла есть текст, отображаем его в правой колонке
        if element.text and element.text.strip():
            self.tree.item(node_id, values=(element.text.strip(),))
            # Добавляем дочерний узел с текстом
            self.tree.insert(node_id, "end", text="#text", values=(element.text.strip(),))

        # Добавляем атрибуты как дочерние узлы
        for attr_name, attr_value in element.attrib.items():
            self.tree.insert(node_id, "end", text=f"@{attr_name}", values=(attr_value,), tags=("attribute",))

        # Рекурсивно добавляем дочерние узлы
        for child in element:
            self.display_xml(child, node_id)

    def display_json(self, data, parent=""):
        if isinstance(data, dict):
            for key, value in data.items():
                node_id = self.tree.insert(parent, "end", text=key, values=("",))
                self.display_json(value, node_id)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                node_id = self.tree.insert(parent, "end", text=f"[{index}]", values=("",))
                self.display_json(value, node_id)
        else:
            # Если это значение, добавляем его как текст
            self.tree.item(parent, values=(data,))

    def on_double_click(self, event):
        self.edit_node()

    def on_tree_open(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        if values and values[0]:  # Если есть значение в правой колонке
            existing_children = {self.tree.item(child, "text") for child in self.tree.get_children(selected_item)}
            if "#text" not in existing_children:
                # Добавляем дочерний узел с текстом, если его нет
                self.tree.insert(selected_item, "end", text="#text", values=(values[0],))
            # Убираем значение из правой колонки родительского узла
            self.tree.item(selected_item, values=("",))

    def on_tree_close(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        # Проверяем, есть ли дочерний узел #text
        for child in self.tree.get_children(selected_item):
            if self.tree.item(child, "text") == "#text":
                # Возвращаем текст в правую колонку родительского узла
                text_value = self.tree.item(child, "values")[0] if self.tree.item(child, "values") else ""
                self.tree.item(selected_item, values=(text_value,))
                # НЕ удаляем дочерний узел, чтобы его можно было снова открыть

    def get_tree_path(self, item):
        path = []
        while item:
            node_text = self.tree.item(item, "text")
            path.insert(0, node_text)
            item = self.tree.parent(item)
        return path

    def get_data_from_path(self, path):
        data = self.editor.data
        for key in path:
            if self.editor.file_type == "JSON":
                if isinstance(data, dict):
                    data = data.get(key)
                elif isinstance(data, list):
                    try:
                        index = int(key.strip("[]"))
                        data = data[index]
                    except (ValueError, IndexError):
                        return None
            elif self.editor.file_type == "XML":
                if isinstance(data, ET.Element):
                    if key.startswith("@"):
                        # Атрибут
                        attr_name = key[1:]
                        return data.attrib.get(attr_name)
                    elif key == "#text":
                        return data.text
                    else:
                        data = next((child for child in data if child.tag == key), None)
                else:
                    return None
            if data is None:
                return None
        return data

    def get_xml_element_by_path(self, item):
        path = self.get_tree_path(item)
        data = self.editor.data
        for key in path:
            if key.startswith("@") or key == "#text":
                return None  # Атрибуты и текст не являются элементами
            data = next((child for child in data if child.tag == key), None)
            if data is None:
                break
        return data
