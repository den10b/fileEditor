# view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.details_entries = None
        self.details_labels = None
        self.tree = None
        self.controller = None
        self.title("XML и JSON Редактор")
        self.geometry("1200x700")
        self.current_file_type = None  # 'json' или 'xml'
        self.create_widgets()

    def create_widgets(self):
        self.create_menu()
        self.create_toolbar()
        self.create_paned_window()
        self.create_context_menu()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть JSON", command=lambda: self.on_open("json"))
        file_menu.add_command(label="Открыть XML", command=lambda: self.on_open("xml"))
        file_menu.add_command(label="Сохранить", command=self.on_save)
        file_menu.add_command(label="Сохранить как...", command=lambda: self.on_save(as_new=True))
        file_menu.add_separator()
        file_menu.add_command(label="Выйти", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Добавить ...", command=self.on_add_node)
        edit_menu.add_separator()
        edit_menu.add_command(label="Удалить", command=self.on_delete_node)
        menubar.add_cascade(label="Правка", menu=edit_menu)

        # Меню "Валидация"
        validate_menu = tk.Menu(menubar, tearoff=0)
        validate_menu.add_command(label="Валидировать текущий документ", command=lambda: self.on_validate("current"))
        validate_menu.add_command(label="Валидировать другой документ", command=lambda: self.on_validate("other"))
        menubar.add_cascade(label="Валидация", menu=validate_menu)

        self.config(menu=menubar)

    def create_toolbar(self):
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)

        add_node_btn = tk.Button(toolbar, text="Добавить ...", command=self.on_add_node)
        add_node_btn.pack(side=tk.LEFT, padx=2, pady=2)

        validate_btn = tk.Button(toolbar, text="Валидировать", command=lambda: self.on_validate("current"))
        validate_btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_paned_window(self):
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Левая панель: TreeView
        self.create_tree_view(paned_window)

        # Правая панель: Details
        self.create_details_panel(paned_window)

    def create_tree_view(self, paned_window):
        tree_frame = ttk.Frame(paned_window, width=400)
        paned_window.add(tree_frame, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("Value",), show="tree headings")
        self.tree.heading("#0", text="Ключ")
        self.tree.heading("Value", text="Значение")
        self.tree.column("#0", width=300, anchor='w')
        self.tree.column("Value", width=300, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_details_panel(self, paned_window):
        details_frame = ttk.Frame(paned_window, width=600)
        paned_window.add(details_frame, weight=3)

        fields = ["Ключ", "Значение", "Тип"]
        self.details_entries = {}
        for idx, field in enumerate(fields):
            label = ttk.Label(details_frame, text=field + ":")
            label.grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)
            match field:
                case "Тип":
                    self.type_var = tk.StringVar()
                    self.type_dropdown = ttk.Combobox(details_frame, textvariable=self.type_var, state="readonly")
                    self.type_dropdown.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
                case _:
                    entry = ttk.Entry(details_frame, width=50)
                    entry.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
                    self.details_entries[field] = entry

        save_btn = ttk.Button(details_frame, text="Сохранить изменения", command=self.on_save_details)
        save_btn.grid(row=len(fields), column=1, sticky=tk.E, padx=5, pady=10)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Добавить узел", command=self.on_add_node)
        self.context_menu.add_command(label="Добавить атрибут", command=self.on_add_attribute)
        self.context_menu.add_command(label="Добавить комментарий", command=self.on_add_comment)
        self.context_menu.add_command(label="Добавить инструкцию обработки", command=self.on_add_pi)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить узел", command=self.on_delete_node)
        self.context_menu.add_command(label="Изменить узел", command=self.on_edit_node)

    def bind_shortcuts(self):
        self.bind_all("<Control-o>", lambda event: self.on_open("json"))
        self.bind_all("<Control-O>", lambda event: self.on_open("json"))
        self.bind_all("<Control-s>", lambda event: self.on_save())
        self.bind_all("<Control-S>", lambda event: self.on_save())
        self.bind_all("<Control-a>", lambda event: self.on_add_node())
        self.bind_all("<Control-A>", lambda event: self.on_add_node())
        self.bind_all("<Delete>", lambda event: self.on_delete_node())

    # Методы для привязки контроллера
    def set_controller(self, controller):
        self.controller = controller

    def show_xml_controls(self):
        # Показать кнопки, специфичные для XML
        self.add_comment_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_pi_btn.pack(side=tk.LEFT, padx=2, pady=2)

    def hide_xml_controls(self):
        # Скрыть кнопки, специфичные для XML
        self.add_comment_btn.pack_forget()
        self.add_pi_btn.pack_forget()

    def show_json_controls(self):
        # Показать кнопки, специфичные для JSON
        pass  # Если есть специфичные кнопки для JSON, добавьте их

    def hide_json_controls(self):
        # Скрыть кнопки, специфичные для JSON
        pass

    def on_open(self, file_type):
        self.controller.open_file(file_type)

    def on_save(self, as_new=False):
        self.controller.save_file(as_new)

    def on_add_node(self):
        self.on_add_node_dialog()

    def on_add_attribute(self):
        self.controller.add_attribute()

    def on_add_comment(self):
        self.controller.add_comment()

    def on_add_pi(self):
        self.controller.add_processing_instruction()

    def on_delete_node(self):
        self.controller.delete_node()

    def on_edit_node(self):
        self.controller.edit_node()

    def on_validate(self, target):
        self.controller.validate(target)

    def on_double_click(self, event):
        self.controller.edit_node()

    def on_edit_xml_declaration(self):
        self.controller.edit_xml_declaration()

    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = selected_item[0]
            self.controller.display_details(item)

    def on_add_node_dialog(self):
        if not self.current_file_type:
            self.show_error("Ошибка", "Сначала откройте файл XML или JSON.")
            return

        # Окно выбора типа
        dialog = tk.Toplevel(self)
        dialog.title("Выберите тип узла")
        dialog.geometry("300x200")

        # Доступные типы для JSON и XML
        if self.current_file_type == "json":
            types = [("Узел", "node"), ("Список", "list"), ("Число", "number"), ("Строка", "string"),
                     ("Булево", "boolean"), ("Null", "null")]
        elif self.current_file_type == "xml":
            types = [("Узел", "node"), ("Атрибут", "attribute"), ("Комментарий", "comment"),
                     ("Инструкция обработки", "pi")]

        # Добавляем кнопки для каждого типа
        for text, type_ in types:
            button = ttk.Button(dialog, text=text, command=lambda t=type_: self.on_type_selected(dialog, t))
            button.pack(pady=5)

        # Кнопка отмены
        cancel_btn = ttk.Button(dialog, text="Отмена", command=dialog.destroy)
        cancel_btn.pack(pady=5)

    # Метод вызывается при выборе типа узла
    def on_type_selected(self, dialog, node_type):
        dialog.destroy()
        self.on_add_node_type(node_type)

    def on_add_node_type(self, node_type):
        dialog = tk.Toplevel(self)
        dialog.title(f"Добавление узла: {node_type}")
        dialog.geometry("400x300")

        # Поля для ввода данных
        key_label = ttk.Label(dialog, text="Ключ:")
        key_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        key_entry = ttk.Entry(dialog, width=40)
        key_entry.grid(row=0, column=1, padx=5, pady=5)

        value_label = ttk.Label(dialog, text="Значение:")
        value_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        value_entry = ttk.Entry(dialog, width=40)
        value_entry.grid(row=1, column=1, padx=5, pady=5)

        # Для XML: скрываем поле значения для атрибута, комментария или инструкции обработки
        if self.current_file_type == "xml" and node_type in ["attribute", "comment", "pi"]:
            value_entry.grid_remove()

        # Кнопка подтверждения
        add_btn = ttk.Button(dialog, text="Добавить",
                             command=lambda: self.add_node_action(dialog, key_entry, value_entry, node_type))
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Кнопка отмены
        cancel_btn = ttk.Button(dialog, text="Отмена", command=dialog.destroy)
        cancel_btn.grid(row=3, column=0, columnspan=2, pady=5)

    # Метод для завершения добавления узла
    def add_node_action(self, dialog, key_entry, value_entry, node_type):
        key = key_entry.get()
        value = value_entry.get() if value_entry.winfo_ismapped() else None
        dialog.destroy()
        self.controller.add_node_action(key, value, node_type)

    def on_save_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_error("Ошибка", "Нет выбранного узла для сохранения изменений.")
            return

        item = selected_item[0]
        path = self.controller.get_path_from_tree_item(item)  # Получаем путь
        key = self.details_entries["Ключ"].get()
        value = self.details_entries["Значение"].get()
        type_ = self.type_var.get()

        # Если значение - число, преобразуем
        if type_ == "number":
            value = int(value)
        elif type_ == "boolean":
            value = value.lower() == "true"
        elif type_ == "null":
            value = None

        self.controller.update_node(path, key, value, type_)

    # Методы для обновления интерфейса
    def populate_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        self._populate_tree_recursive("", data)

    def _populate_tree_recursive(self, parent, data):
        match self.current_file_type:
            case "xml":
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key.startswith('@'):
                            # Атрибуты
                            display_key = key
                            display_value = value
                            self.tree.insert(parent, 'end', text=display_key, values=(display_value,), tags=('attribute', key))
                        elif key == '#comment':
                            for comment in value:
                                self.tree.insert(parent, 'end', text="#comment", values=(comment,), tags=('comment',))
                        # elif key == '#processing_instruction':
                        #     for pi in value:
                        #         self.tree.insert(parent, 'end', text="#processing_instruction", values=(pi,),
                        #                          tags=('processing_instruction',))
                        elif key == '#text':
                            # TODO: тут можно родителю текст давать
                            self.tree.insert(parent, 'end', text="#text", values=(value,), tags=('text',))
                        elif isinstance(value, dict):
                            node = self.tree.insert(parent, 'end', text=key, values=("",), tags=('node',))
                            self._populate_tree_recursive(node, value)
                        else:
                            self.tree.insert(parent, 'end', text=key, values=(value,), tags=('node',))
                else:
                    self.tree.insert(parent, 'end', text="Value", values=(data,), tags=('value',))
            case "json":
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            node = self.tree.insert(parent, 'end', text=key, values=("",), tags=('node',))
                            for index, item in enumerate(value):
                                child = self.tree.insert(node, 'end', text=f"[{index}]", values=("",), tags=('list',))
                                self._populate_tree_recursive(child, item)
                        elif isinstance(value, dict):
                            node = self.tree.insert(parent, 'end', text=key, values=("",), tags=('node',))
                            self._populate_tree_recursive(node, value)
                        else:
                            tag = self.get_json_type_tag(value)
                            self.tree.insert(parent, 'end', text=key, values=(value,), tags=(tag,))
                elif isinstance(data, list):
                    # JSON массив на верхнем уровне
                    for index, item in enumerate(data):
                        node = self.tree.insert(parent, 'end', text=f"[{index}]", values=(""), tags=('list',))
                        self._populate_tree_recursive(node, item)
                else:
                    self.tree.insert(parent, 'end', text="Value", values=(data,), tags=('value',))
        self.apply_tags_colors()

    def format_json_value(self, value):
        if isinstance(value, str):
            # return f"\"{value}\""
            return f"{value}"
        elif isinstance(value, bool):
            return str(value).lower()
        elif value is None:
            return "null"
        else:
            return str(value)

    def get_json_type_tag(self, value):
        if isinstance(value, str):
            return 'string'
        elif isinstance(value, bool):
            return 'boolean'
        elif value is None:
            return 'null'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, dict):
            return 'object'
        elif isinstance(value, list):
            return 'array'
        else:
            return 'unknown'

    def apply_tags_colors(self):
        self.tree.tag_configure('node', foreground='black')
        self.tree.tag_configure('attribute', foreground='firebrick')
        self.tree.tag_configure('comment', foreground='green')
        self.tree.tag_configure('processing_instruction', foreground='purple')
        self.tree.tag_configure('text', foreground='grey')
        self.tree.tag_configure('list', foreground='orange')
        self.tree.tag_configure('string', foreground='blue3')
        self.tree.tag_configure('number', foreground='chartreuse4')
        self.tree.tag_configure('boolean', foreground='dodgerblue3')
        self.tree.tag_configure('null', foreground='darkseagreen4', font=('TkDefaultFont', 10, 'italic'))
        self.tree.tag_configure('object', foreground='teal')
        self.tree.tag_configure('array', foreground='olive')
        self.tree.tag_configure('unknown', foreground='black')

    def display_details(self, item):
        details = self.controller.get_node_details(item)

        self.details_entries["Ключ"].delete(0, tk.END)
        self.details_entries["Ключ"].insert(0, details["key"])

        self.details_entries["Значение"].delete(0, tk.END)
        self.details_entries["Значение"].insert(0, details["value"])

        self.type_dropdown['values'] = self.controller.get_available_types()
        self.type_var.set(details["type"])

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def prompt_user(self, prompt, initialvalue=""):
        return simpledialog.askstring("Ввод", prompt, initialvalue=initialvalue)
