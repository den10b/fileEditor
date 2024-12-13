from tkinter import Frame, Menu, PanedWindow, messagebox, simpledialog, ttk, filedialog
from file_handler import FileHandler
from lxml import etree
from editor import JSONNode


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
        self.tree.tag_configure("comment", foreground="green")
        self.tree.tag_configure("cdata", foreground="brown")
        self.tree.tag_configure("processing", foreground="purple")

        self.toolbar = None
        # Панель инструментов
        self.create_toolbar(root)

        # Меню
        self.create_menu(root)

    def create_menu(self, root):
        menubar = Menu(root)
        menubar.add_command(label="Открыть", command=self.open_file)
        menubar.add_command(label="Сохранить", command=self.save_file)
        root.config(menu=menubar)

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
                ttk.Button(toolbar, text="Добавить Комментарий", command=self.add_comment).pack(side="left", padx=2,
                                                                                                pady=2)
                ttk.Button(toolbar, text="Добавить CDATA", command=self.add_cdata).pack(side="left", padx=2, pady=2)
                ttk.Button(toolbar, text="Добавить Инструкцию", command=self.add_processing_instruction).pack(
                    side="left", padx=2, pady=2)
                ttk.Button(toolbar, text="Добавить атрибут", command=self.add_attribute).pack(side="left", padx=2,
                                                                                              pady=2)
            toolbar.pack(side="top", fill="x")
            self.toolbar = toolbar

    def add_attribute(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите родительский узел для добавления атрибута.")
            return

        attr_key = simpledialog.askstring("Добавить атрибут", "Введите название атрибута:")
        if not attr_key:
            return
        attr_val = simpledialog.askstring("Добавить атрибут", "Введите значение атрибута:")
        if not attr_val:
            return

        parent_node = self.get_struct_from_iid(selected_item)
        if isinstance(parent_node, etree._Element):
            parent_node.set(attr_key, attr_val)
            self.refresh_ui()

    def add_comment(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите родительский узел для добавления комментария.")
            return

        comment_text = simpledialog.askstring("Добавить Комментарий", "Введите текст комментария:")
        if not comment_text:
            return

        parent_node = self.get_struct_from_iid(selected_item)
        if isinstance(parent_node, etree._Element):
            comment = etree.Comment(comment_text)
            parent_node.append(comment)
            self.refresh_ui()

    def add_cdata(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите родительский узел для добавления CDATA.")
            return

        cdata_text = simpledialog.askstring("Добавить CDATA", "Введите текст CDATA:")
        if not cdata_text:
            return

        parent_node = self.get_struct_from_iid(selected_item)
        if isinstance(parent_node, etree._Element):
            cdata = etree.CDATA(cdata_text)
            parent_node.append(cdata)
            self.refresh_ui()

    def add_processing_instruction(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите родительский узел для добавления инструкции обработки.")
            return

        target = simpledialog.askstring("Добавить Инструкцию", "Введите target:")
        content = simpledialog.askstring("Добавить Инструкцию", "Введите содержание инструкции:")
        if not target or not content:
            return

        parent_node = self.get_struct_from_iid(selected_item)
        if isinstance(parent_node, etree._Element):
            pi = etree.ProcessingInstruction(target, content)
            parent_node.addprevious(pi)  # Инструкции добавляются перед элементами
            self.refresh_ui()

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
        print(struct_obj)
        print(type(struct_obj))
        print(tree_id)
        print(type(tree_id))
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
        print(data)
        print(parent)
        print(type(data))
        match type(data):
            case etree._Element:
                self._display_xml_node(data, parent)
            case dict() | list():
                self._display_json_node(data, parent)
            # case JSONNode:
            #     self._display_json_node(data, parent)
            case _:
                if isinstance(data, JSONNode):
                    self._display_json_node(data, parent)
                else:
                    self.tree.item(parent, values=(data,))

    def _display_xml_node(self, element, parent):
        if parent == "":
            declaration = self.file_handler.editor.get_meta()
            if declaration:
                self.tree.insert("", "end", text="xml", values=(declaration,))
        node_id = None
        print(type(element))

        match type(element):
            case etree._Element:
                node_id = self.tree.insert(parent, "end", text=element.tag, values=("",), tags=("node",))
            case etree._ProcessingInstruction:
                print(element)
                node_id = self.tree.insert(parent, "end", text=element.target, values=(element.text,),
                                           tags=("processing",))
            case etree._Comment:
                print(element)
                node_id = self.tree.insert(parent, "end", text="#comment", values=(element.text,), tags=("comment",))
            case etree.CDATA:
                node_id = self.tree.insert(parent, "end", text="#cdata", values=(element.text,), tags=("cdata",))

        self.add_node_to_map(element, node_id)

        # Добавление текста, атрибутов и дочерних элементов
        if element.text and element.text.strip() and type(element) is etree._Element:
            raw_string = etree.tostring(element, encoding="unicode")
            if "<![CDATA[" in raw_string:
                self.tree.item(node_id, values=(element.text.strip(),))
                self.tree.insert(node_id, "end", text="#cdata", values=(element.text.strip(),), tags=("cdata",))
            else:
                self.tree.item(node_id, values=(element.text.strip(),))
                self.tree.insert(node_id, "end", text="#text", values=(element.text.strip(),), tags=("text",))
        for attr_name, attr_value in element.attrib.items():
            self.tree.insert(node_id, "end", text=f"@{attr_name}", values=(attr_value,), tags=("attribute",))
        for child in element:
            self.display_node(child, node_id)

    def _display_json_node(self, node, parent):
        print(node)
        print(parent)
        print(type(node.value))
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
            if ("#text" or "#cdata") not in existing_children:
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
