# ui.py
from tkinter import Frame, Menu, PanedWindow, messagebox, simpledialog, ttk, filedialog
from file_handler import FileHandler
from editor import BaseEditor  # Импорт базового класса для типизации (если необходимо)
import json
from lxml import etree

from utils import get_expanded_paths, set_expanded_paths


class EditorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML/JSON Editor")

        # Инициализация обработчика файлов
        self.file_handler = FileHandler()

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
        self.tree.bind("<ButtonPress-3>",self.on_rmb)
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
        menubar.add_command(label="Открыть", command=self.open_file)
        menubar.add_command(label="Сохранить", command=self.save_file)
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
            filetypes=[("XML/JSON файлы", "*.xml *.json")]
        )
        if filepath:
            self.file_handler.save_file(filepath)

    def add_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для добавления.")
            return

        # Запрос имени нового узла
        new_node_name = simpledialog.askstring("Добавить узел", "Введите имя нового узла:")
        if not new_node_name:
            return

        parent_path = self.get_tree_path(selected_item)  # Путь к родительскому узлу
        parent_data = self.get_data_from_path(parent_path)

        if isinstance(parent_data, etree._Element):  # XML
            # Добавляем новый элемент в родительские данные
            new_element = etree.SubElement(parent_data, new_node_name)
        elif isinstance(parent_data, (dict, list)):  # JSON
            # Добавляем новый элемент в JSON-структуру
            self.file_handler.editor.add_node(parent_data, new_node_name)

        # Добавляем новый узел в дерево
        new_node_id = self.tree.insert(
            selected_item, "end", text=new_node_name, values=(""), open=False
        )

        # Обновляем родительский узел (делаем его раскрываемым)
        self.tree.item(selected_item, open=True)

    def delete_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для удаления.")
            return

        parent_item = self.tree.parent(selected_item)
        parent_path = self.get_tree_path(parent_item)
        parent_data = self.get_data_from_path(parent_path)

        current_node = self.tree.item(selected_item, "text")
        child_data = self.get_data_from_path(self.get_tree_path(selected_item))

        # Удаляем узел из данных
        if isinstance(parent_data, etree._Element):  # XML
            parent_data.remove(child_data)
        elif isinstance(parent_data, (dict, list)):  # JSON
            self.file_handler.editor.delete_node(parent_data, current_node)

        # Удаляем узел из дерева
        self.tree.delete(selected_item)

        # Если родительский узел остался пустым, помечаем его как лист
        if not self.tree.get_children(parent_item):
            self.tree.item(parent_item, open=False)

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

        self.tree.item(selected_item, values=(new_value,))

        current_path = self.get_tree_path(selected_item)
        current_data = self.get_data_from_path(current_path)

        parent_item = self.tree.parent(selected_item)
        parent_path = self.get_tree_path(parent_item)
        parent_data = self.get_data_from_path(parent_path)

        # Обновляем значение в редакторе
        if isinstance(parent_data, dict):
            parent_data[current_value] = new_value
        elif isinstance(parent_data, list):
            try:
                index = int(current_value.strip("[]"))
                parent_data[index] = new_value
            except ValueError:
                pass

        self.refresh_ui()

    def refresh_ui(self, parent_node=None):
        if parent_node is None:  # Полное обновление дерева
            expanded_paths = get_expanded_paths(self.tree)
            self.tree.delete(*self.tree.get_children())
            if self.file_handler.file_type == "XML":
                self.display_xml(self.file_handler.editor.data)
            elif self.file_handler.file_type == "JSON":
                self.display_json(self.file_handler.editor.data)
            set_expanded_paths(self.tree, expanded_paths)
        else:
            # Обновляем только конкретный узел
            parent_path = self.get_tree_path(parent_node)
            parent_data = self.get_data_from_path(parent_path)
            self.tree.delete(*self.tree.get_children(parent_node))

            if isinstance(parent_data, etree._Element):
                self.display_xml(parent_data, parent_node)
            elif isinstance(parent_data, (dict, list)):
                self.display_json(parent_data, parent_node)

    def display_xml(self, element, parent=""):
        if parent == "":
            declaration = self.file_handler.editor.get_meta()
            if declaration:
                self.tree.insert("", "end", text="xml", values=(declaration,))

        node_id = self.tree.insert(parent, "end", text=element.tag, values=(""))

        # Если есть текст внутри элемента
        if element.text and element.text.strip():
            self.tree.insert(node_id, "end", text="#text", values=(element.text.strip(),))

        # Добавляем атрибуты элемента как дочерние узлы
        for attr_name, attr_value in element.attrib.items():
            self.tree.insert(node_id, "end", text=f"@{attr_name}", values=(attr_value,), tags=("attribute",))

        # Добавляем CDATA
        if isinstance(element.text, etree.CDATA):
            self.tree.insert(node_id, "end", text="#cdata-section", values=(element.text.strip(),))

        # Рекурсивно добавляем дочерние узлы
        for child in element:
            self.display_xml(child, node_id)

        # Если у узла есть дочерние элементы, делаем его "раскрываемым"
        if len(element):
            self.tree.item(node_id, open=False)

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

    def save_tree_state(self):
        state = {}
        for item in self.tree.get_children():
            state[item] = self.tree.item(item, "open")
            state.update(self._save_subtree_state(item))
        return state

    def _save_subtree_state(self, item):
        state = {}
        for child in self.tree.get_children(item):
            state[child] = self.tree.item(child, "open")
            state.update(self._save_subtree_state(child))
        return state

    def restore_tree_state(self, state):
        for item, is_open in state.items():
            if self.tree.exists(item):
                self.tree.item(item, open=is_open)

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
        data = self.file_handler.editor.data
        for key in path:
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list):
                try:
                    index = int(key.strip("[]"))
                    data = data[index]
                except (ValueError, IndexError):
                    return None
            elif isinstance(data, etree._Element):
                if key.startswith("@"):
                    # Атрибут
                    attr_name = key[1:]
                    data = data.attrib.get(attr_name)
                elif key == "#text":
                    data = data.text
                else:
                    data = next((child for child in data if child.tag == key), None)
            if data is None:
                return None
        return data

    def on_double_click(self, event):
        self.edit_node()
    def on_rmb(self, event):
        print(event)