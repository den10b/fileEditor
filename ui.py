from tkinter import Frame, Menu, PanedWindow, messagebox, simpledialog, ttk, filedialog
from file_handler import FileHandler
from lxml import etree


class EditorUI:
    def __init__(self, root):
        self.node_map = {}  # Связь между объектами структуры и TreeView
        self.root = root
        self.root.title("XML/JSON Editor")
        self.file_handler = FileHandler()

        # Основное окно
        self.main_frame = PanedWindow(root, orient="horizontal")
        self.main_frame.pack(fill="both", expand=True)

        # Древовидная структура
        self.tree = ttk.Treeview(self.main_frame, columns=("Value",), show="tree headings")
        self.tree.heading("#0", text="Node")
        self.tree.heading("Value", text="Value")
        self.tree.column("#0", anchor="w", width=200, stretch=True)
        self.tree.column("Value", anchor="w", width=300, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.main_frame.add(self.tree)

        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewClose>>", self.on_tree_close)

        # Стиль для атрибутов
        style = ttk.Style()
        style.configure("Treeview.tag.Attribute", foreground="blue")
        self.tree.tag_configure("attribute", foreground="blue")

        self.toolbar = None
        # Панель инструментов
        self.create_toolbar(root)

        # Меню
        self.create_menu(root)

    def create_toolbar(self, root):
        if self.toolbar:
            self.toolbar.pack_forget()
        if self.file_handler.file_type:
            toolbar = Frame(root, bd=1, relief="raised")
            ttk.Button(toolbar, text="Добавить узел", command=self.add_node).pack(side="left", padx=2, pady=2)
            ttk.Button(toolbar, text="Удалить узел", command=self.delete_node).pack(side="left", padx=2, pady=2)
            ttk.Button(toolbar, text="Редактировать узел", command=self.edit_node).pack(side="left", padx=2, pady=2)
            ttk.Button(toolbar, text="Редактировать значение узла", command=self.edit_node_value).pack(side="left",
                                                                                                       padx=2, pady=2)

            if self.file_handler.file_type == "XML":
                ttk.Button(toolbar, text="Добавить 1").pack(side="left", padx=2, pady=2)
                ttk.Button(toolbar, text="Добавить 2").pack(side="left", padx=2, pady=2)
                ttk.Button(toolbar, text="Добавить 3").pack(side="left", padx=2, pady=2)
            toolbar.pack(side="top", fill="x")
            self.toolbar = toolbar

    def create_menu(self, root):
        menubar = Menu(root)
        menubar.add_command(label="Открыть", command=self.open_file)
        menubar.add_command(label="Сохранить", command=self.save_file)
        root.config(menu=menubar)

    def open_file(self):
        filepath = self.file_handler.open_file()
        self.create_toolbar(self.root)
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

    def add_node_to_map(self, struct_obj, tree_id):
        """Добавление объекта структуры и TreeView в связку"""
        self.node_map[struct_obj] = tree_id
        self.node_map[tree_id] = struct_obj

    def get_struct_from_iid(self, tree_id):
        """Получение объекта структуры по TreeView ID"""
        return self.node_map.get(tree_id)

    def get_iid_from_struct(self, struct_obj):
        """Получение TreeView ID по объекту структуры"""
        return self.node_map.get(struct_obj)

    def clean_map(self):
        for k, v in self.node_map:
            if not isinstance(k, etree._Element):
                self.node_map.pop(k)

    def refresh_ui(self):
        # self.clean_map()
        self.tree.delete(*self.tree.get_children())
        match self.file_handler.file_type:
            case "XML":
                self.display_node(self.file_handler.editor.data)
            case "JSON":
                self.display_node(self.file_handler.editor.data)

    def display_node(self, data, parent=""):
        if isinstance(data, etree._Element):  # XML
            self._display_xml_node(data, parent)
        elif isinstance(data, (dict, list)):  # JSON
            self._display_json_node(data, parent)
        else:
            self.tree.item(parent, values=(data,))

    def _display_xml_node(self, element, parent):

        if parent == "":
            declaration = self.file_handler.editor.get_meta()
            if declaration:
                self.tree.insert("", "end", text="xml", values=(declaration,))

        node_id = self.tree.insert(parent, "end", text=element.tag, values=("",), tags=("node",))
        self.add_node_to_map(element, node_id)

        # Добавление текста, атрибутов и дочерних элементов
        if element.text and element.text.strip():
            self.tree.item(node_id, values=(element.text.strip(),))
            self.tree.insert(node_id, "end", text="#text", values=(element.text.strip(),), tags=("text",))
        for attr_name, attr_value in element.attrib.items():
            self.tree.insert(node_id, "end", text=f"@{attr_name}", values=(attr_value,), tags=("attribute",))
        for child in element:
            self.display_node(child, node_id)

    def _display_json_node(self, node, parent):
        node_id = self.tree.insert(
            parent,
            "end",
            text=node.key if node.key != "root" else "JSON",
            values=(node.value if node.is_leaf() else "",)
        )
        self.add_node_to_map(node, node_id)

        # Рекурсивно добавляем детей
        for child in node.children:
            self._display_json_node(child, node_id)

    def add_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для добавления.")
            return

        new_node_name = simpledialog.askstring("Добавить узел", "Введите имя нового узла:")
        if not new_node_name:
            return

        parent_node = self.get_struct_from_iid(selected_item)

        if parent_node:
            self.file_handler.editor.add_node(parent_node, new_node_name)
            self.refresh_ui()
        else:
            messagebox.showerror("Ошибка", "Не удалось найти родительский узел.")

    def delete_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для удаления.")
            return

        parent_item = self.tree.parent(selected_item)
        parent_data = self.get_struct_from_iid(parent_item)

        to_delete = None

        if isinstance(parent_data, dict):
            key_to_delete = self.tree.item(selected_item, "text")
            to_delete = key_to_delete
        elif isinstance(parent_data, list):
            index_to_delete = int(self.tree.item(selected_item, "text").strip("[]"))
            to_delete = index_to_delete
        elif isinstance(parent_data, etree._Element):
            current_data = self.get_struct_from_iid(selected_item)
            to_delete = current_data

        self.file_handler.editor.delete_node(parent_data, to_delete)
        self.refresh_ui()

    def edit_node_value(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для редактирования.")
            return

        current_value = self.tree.item(selected_item, "values")
        if len(current_value) < 1:
            current_value = ""
        else:
            current_value = current_value[0]
        new_value = simpledialog.askstring("Редактировать", "Введите новое значение:", initialvalue=current_value)
        if not new_value:
            return

        parent_item = self.tree.parent(selected_item)
        parent_data = self.get_struct_from_iid(parent_item)

        if isinstance(parent_data, dict):
            parent_data[new_value] = parent_data.pop(current_value)
        elif isinstance(parent_data, list):
            index = int(current_value.strip("[]"))
            parent_data[index] = new_value
        elif isinstance(parent_data, etree._Element):
            current_data = self.get_struct_from_iid(selected_item)
            current_data.text = new_value

        self.refresh_ui()

    def edit_node(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите узел для редактирования.")
            return

        current_value = self.tree.item(selected_item, "text")
        new_value = simpledialog.askstring("Редактировать", "Введите новое значение:", initialvalue=current_value)
        if not new_value:
            return

        parent_item = self.tree.parent(selected_item)
        parent_data = self.get_struct_from_iid(parent_item)

        if isinstance(parent_data, dict):
            parent_data[new_value] = parent_data.pop(current_value)
        elif isinstance(parent_data, list):
            index = int(current_value.strip("[]"))
            parent_data[index] = new_value
        elif isinstance(parent_data, etree._Element):
            current_data = self.get_struct_from_iid(selected_item)
            current_data.tag = new_value

        self.refresh_ui()

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
