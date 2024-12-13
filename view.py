# view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XML и JSON Редактор")
        self.geometry("1200x700")
        self.current_file_type = None  # 'json' или 'xml'
        self.create_widgets()

    def create_widgets(self):
        # Создание меню
        menubar = tk.Menu(self)
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть JSON", command=lambda: self.on_open("json"))
        file_menu.add_command(label="Открыть XML", command=lambda: self.on_open("xml"))
        file_menu.add_command(label="Сохранить", command=self.on_save)
        file_menu.add_command(label="Сохранить как...", command=lambda: self.on_save(as_new=True))
        file_menu.add_separator()
        file_menu.add_command(label="Выйти", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Добавить узел", command=self.on_add_node)
        edit_menu.add_command(label="Добавить атрибут", command=self.on_add_attribute)
        edit_menu.add_command(label="Добавить комментарий", command=self.on_add_comment)
        edit_menu.add_command(label="Добавить инструкцию обработки", command=self.on_add_pi)
        edit_menu.add_separator()
        edit_menu.add_command(label="Удалить узел", command=self.on_delete_node)
        edit_menu.add_command(label="Изменить узел", command=self.on_edit_node)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        # Меню Валидация
        validate_menu = tk.Menu(menubar, tearoff=0)
        validate_menu.add_command(label="Валидировать текущий документ", command=lambda: self.on_validate("current"))
        validate_menu.add_command(label="Валидировать другой документ", command=lambda: self.on_validate("other"))
        menubar.add_cascade(label="Валидация", menu=validate_menu)
        self.config(menu=menubar)

        # Панель инструментов
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        # Кнопки панели инструментов
        add_node_btn = tk.Button(toolbar, text="Добавить узел", command=self.on_add_node)
        add_node_btn.pack(side=tk.LEFT, padx=2, pady=2)
        add_attr_btn = tk.Button(toolbar, text="Добавить атрибут", command=self.on_add_attribute)
        add_attr_btn.pack(side=tk.LEFT, padx=2, pady=2)
        add_comment_btn = tk.Button(toolbar, text="Добавить комментарий", command=self.on_add_comment)
        add_comment_btn.pack(side=tk.LEFT, padx=2, pady=2)
        add_pi_btn = tk.Button(toolbar, text="Добавить инструкцию", command=self.on_add_pi)
        add_pi_btn.pack(side=tk.LEFT, padx=2, pady=2)
        delete_node_btn = tk.Button(toolbar, text="Удалить узел", command=self.on_delete_node)
        delete_node_btn.pack(side=tk.LEFT, padx=2, pady=2)
        edit_node_btn = tk.Button(toolbar, text="Изменить узел", command=self.on_edit_node)
        edit_node_btn.pack(side=tk.LEFT, padx=2, pady=2)
        validate_btn = tk.Button(toolbar, text="Валидировать", command=lambda: self.on_validate("current"))
        validate_btn.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Создание PanedWindow для разделения области на левую (TreeView) и правую (Details)
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Левая панель: TreeView
        tree_frame = ttk.Frame(paned_window, width=400)
        paned_window.add(tree_frame, weight=1)

        # Настройка TreeView с двумя колонками: Ключ и Значение
        self.tree = ttk.Treeview(tree_frame, columns=("Value",), show="tree headings")
        self.tree.heading("#0", text="Ключ")
        self.tree.heading("Value", text="Значение")
        self.tree.column("#0", width=300, anchor='w')
        self.tree.column("Value", width=300, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Правый клик для контекстного меню

        # Правая панель: Details
        details_frame = ttk.Frame(paned_window, width=600)
        paned_window.add(details_frame, weight=3)

        # Поля для отображения и редактирования деталей выбранного узла
        self.details_labels = {}
        self.details_entries = {}
        self.type_options = {
            'json': ["String", "Number", "Boolean", "Null", "Object", "Array"],
            'xml': ["Attribute", "Comment", "Processing Instruction", "Text", "Node"]
        }
        fields = ["Ключ", "Значение", "Тип"]
        for idx, field in enumerate(fields):
            label = ttk.Label(details_frame, text=field + ":")
            label.grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)
            if field == "Тип":
                self.type_var = tk.StringVar()
                self.type_dropdown = ttk.Combobox(details_frame, textvariable=self.type_var, state="readonly")
                self.type_dropdown.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
            else:
                entry = ttk.Entry(details_frame, width=50)
                entry.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
                self.details_entries[field] = entry

        # Кнопка для сохранения изменений в деталях
        save_btn = ttk.Button(details_frame, text="Сохранить изменения", command=self.on_save_details)
        save_btn.grid(row=len(fields), column=1, sticky=tk.E, padx=5, pady=10)

        # Контекстное меню
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Добавить узел", command=self.on_add_node)
        self.context_menu.add_command(label="Добавить атрибут", command=self.on_add_attribute)
        self.context_menu.add_command(label="Добавить комментарий", command=self.on_add_comment)
        self.context_menu.add_command(label="Добавить инструкцию обработки", command=self.on_add_pi)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить узел", command=self.on_delete_node)
        self.context_menu.add_command(label="Изменить узел", command=self.on_edit_node)

        # Горячие клавиши
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

    def on_open(self, file_type):
        self.controller.open_file(file_type)

    def on_save(self, as_new=False):
        self.controller.save_file(as_new)

    def on_add_node(self):
        self.controller.add_node()

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

    def on_save_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_error("Ошибка", "Нет выбранного узла для сохранения изменений.")
            return
        item = selected_item[0]
        key = self.details_entries["Ключ"].get()
        value = self.details_entries["Значение"].get()
        type_ = self.type_var.get()
        self.controller.update_details(item, key, value, type_)

    # Методы для обновления интерфейса
    def populate_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        self._populate_tree_recursive("", data)

    def _populate_tree_recursive(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith('@'):
                    # Атрибуты
                    display_key = key
                    display_value = value
                    self.tree.insert(parent, 'end', text=display_key, values=(display_value,),
                                     tags=('attribute',))
                elif key == '#comment':
                    for comment in value:
                        display_key = "#comment"
                        display_value = comment
                        self.tree.insert(parent, 'end', text=display_key, values=(display_value,),
                                         tags=('comment',))
                elif key == '#processing_instruction':
                    for pi in value:
                        display_key = "#processing_instruction"
                        display_value = pi
                        self.tree.insert(parent, 'end', text=display_key, values=(display_value,),
                                         tags=('processing_instruction',))
                elif key == '#text':
                    display_key = "#text"
                    display_value = value
                    self.tree.insert(parent, 'end', text=display_key, values=(display_value,),
                                     tags=('text',))
                else:
                    if isinstance(value, list):
                        # Обработка списка элементов (например, несколько <book> или menuitem)
                        for index, item in enumerate(value):
                            if isinstance(item, dict):
                                node = self.tree.insert(parent, 'end', text=key, values=("",), tags=('node',))
                                self._populate_tree_recursive(node, item)
                            else:
                                # Примитивные типы в списках
                                node = self.tree.insert(parent, 'end', text=key, values=(item,), tags=('node',))
                    elif isinstance(value, dict):
                        # Узлы без непосредственного значения
                        node = self.tree.insert(parent, 'end', text=key, values=("",), tags=('node',))
                        self._populate_tree_recursive(node, value)
                    else:
                        # Узлы с непосредственным значением
                        display_value = self.format_json_value(value)
                        tag = self.get_json_type_tag(value)
                        node = self.tree.insert(parent, 'end', text=key, values=(display_value,), tags=(tag,))
        elif isinstance(data, list):
            for index, item in enumerate(data):
                node = self.tree.insert(parent, 'end', text=f"[{index}]", values=("",), tags=('list',))
                self._populate_tree_recursive(node, item)
        else:
            # Для JSON типов значений
            display_key = "Value"
            display_value = self.format_json_value(data)
            tag=self.get_json_type_tag(data)
            self.tree.insert(parent, 'end', text=display_key, values=(display_value,), tags=(tag,))

        # Применение цветовой дифференциации
        self.apply_tags_colors()

    def format_json_value(self, value):
        if isinstance(value, str):
            return f"\"{value}\""
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
        self.tree.tag_configure('attribute', foreground='blue')
        self.tree.tag_configure('comment', foreground='grey')
        self.tree.tag_configure('processing_instruction', foreground='purple')
        self.tree.tag_configure('text', foreground='green')
        self.tree.tag_configure('list', foreground='orange')
        self.tree.tag_configure('string', foreground='brown')
        self.tree.tag_configure('number', foreground='darkred')
        self.tree.tag_configure('boolean', foreground='darkgreen')
        self.tree.tag_configure('null', foreground='black', font=('TkDefaultFont', 10, 'italic'))
        self.tree.tag_configure('object', foreground='teal')
        self.tree.tag_configure('array', foreground='olive')
        self.tree.tag_configure('unknown', foreground='black')

    def display_details(self, item):
        # Получение данных узла
        key = self.tree.item(item, 'text')
        value = self.tree.item(item, 'values')[0]
        tags = self.tree.item(item, 'tags')

        if 'attribute' in tags:
            type_ = "Attribute"
        elif 'comment' in tags:
            type_ = "Comment"
        elif 'processing_instruction' in tags:
            type_ = "Processing Instruction"
        elif 'text' in tags:
            type_ = "Text"
        elif 'string' in tags:
            type_ = "String"
        elif 'number' in tags:
            type_ = "Number"
        elif 'boolean' in tags:
            type_ = "Boolean"
        elif 'null' in tags:
            type_ = "Null"
        elif 'object' in tags:
            type_ = "Object"
        elif 'array' in tags:
            type_ = "Array"
        elif 'list' in tags:
            type_ = "List"
        else:
            type_ = "Node"

        # Установка типов узлов в выпадающий список
        if self.current_file_type == 'json':
            self.type_dropdown['values'] = self.type_options['json']
        elif self.current_file_type == 'xml':
            self.type_dropdown['values'] = self.type_options['xml']
        else:
            self.type_dropdown['values'] = ["Attribute", "Comment", "Processing Instruction", "Node"]

        # Обновление полей деталей
        self.details_entries["Ключ"].delete(0, tk.END)
        self.details_entries["Ключ"].insert(0, key)
        self.details_entries["Значение"].delete(0, tk.END)
        self.details_entries["Значение"].insert(0, value)
        self.type_var.set(type_)

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def prompt_user(self, prompt, initialvalue=""):
        return simpledialog.askstring("Ввод", prompt, initialvalue=initialvalue)
