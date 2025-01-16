# view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


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
        self.buttons = None
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
        edit_menu.add_command(label="Изменить ключ", command=self.on_edit_node_key)
        edit_menu.add_command(label="Изменить значение", command=self.on_edit_node_value)
        edit_menu.add_separator()
        edit_menu.add_command(label="Удалить", command=self.on_delete_node)
        menubar.add_cascade(label="Правка", menu=edit_menu)

        # Меню "Валидация"
        validate_menu = tk.Menu(menubar, tearoff=0)
        validate_menu.add_command(label="Валидировать текущий документ", command=lambda: self.on_validate("current"))
        validate_menu.add_command(label="Валидировать другой документ", command=lambda: self.on_validate("other"))
        validate_menu.add_command(label="Валидировать пароли", command=lambda: self.on_validate("pass"))

        menubar.add_cascade(label="Валидация", menu=validate_menu)

        # Меню "Справка"
        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="О программе", command=self.on_info)
        info_menu.add_command(label="Помощь", command=self.on_help)
        menubar.add_cascade(label="Справка", menu=info_menu)

        self.config(menu=menubar)

    def create_toolbar(self):
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)

        add_node_btn = tk.Button(toolbar, text="Добавить ...", command=self.on_add_node)
        add_node_btn.pack(side=tk.LEFT, padx=2, pady=2)
        edit_key_btn = tk.Button(toolbar, text="Изменить ключ", command=self.on_edit_node_key)
        edit_key_btn.pack(side=tk.LEFT, padx=2, pady=2)
        edit_val_btn = tk.Button(toolbar, text="Изменить значение", command=self.on_edit_node_value)
        edit_val_btn.pack(side=tk.LEFT, padx=2, pady=2)

        validate_btn = tk.Button(toolbar, text="Валидировать", command=lambda: self.on_validate("current"),state="disabled")
        validate_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.buttons = {
            "edit_key_btn": edit_key_btn,
            "edit_val_btn": edit_val_btn,
            "validate_btn": validate_btn,
        }
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
                    self.type_dropdown = ttk.Combobox(details_frame, textvariable=self.type_var, state="readolnly")
                    self.type_dropdown.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
                case _:
                    entry = ttk.Entry(details_frame, width=50, state="readolnly")
                    entry.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=5)
                    self.details_entries[field] = entry

        # save_btn = ttk.Button(details_frame, text="Сохранить изменения", command=self.on_save_details)
        # save_btn.grid(row=len(fields), column=1, sticky=tk.E, padx=5, pady=10)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Добавить ...", command=self.on_add_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Изменить ключ", command=self.on_edit_node_key)
        self.context_menu.add_command(label="Изменить значение", command=self.on_edit_node_value)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить узел", command=self.on_delete_node)

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

    def on_open(self, file_type):
        self.controller.open_file(file_type)

    def on_save(self, as_new=False):
        self.controller.save_file(as_new)

    def on_add_node(self):
        self.on_add_node_dialog()

    def on_delete_node(self):
        self.controller.delete_node()

    def on_edit_node_key(self):
        self.controller.edit_node_key()

    def on_edit_node_value(self):
        self.controller.edit_node_value()

    def on_help(self):
        help_text = (
            f"Инструкция по использованию редактора:\n\n"
            f"- Открытие файла: используйте меню 'Файл' > 'Открыть JSON/XML'.\n"
            f"- Редактирование файла: после открытия файла используйте древовидный интерфейс для выбора узлов. "
            f"Щелкните на узел, чтобы выбрать его, затем выберите желаемое действие на верхней панели "
            f"или в контекстном меню (ПКМ).\n"
            f"- Валидация: в меню 'Валидация' выберите тип проверки. Для 'Валидировать текущий документ' "
            f"выберите схему, соответствующую документу. Для 'Валидировать другой документ' выберите сначала "
            f"файл для валидации, затем файл со схемой. Кнопка 'Валидировать' запускает проверку текущего документа.\n"
            f"- Сохранение: выберите 'Файл' > 'Сохранить' для сохранения изменений или 'Сохранить как...' "
            f"для сохранения с новым именем.\n"
            f"- О программе: нажмите на кнопку 'О программе', чтобы узнать информацию об авторе и версии.\n"
            f"- Подсказки: нажмите на кнопку 'Помощь' для просмотра этой инструкции."
            f"\n"
            f"\n"
            f"После добавления узла невозможно изменить его тип.\n"
            f"Если внутри узла есть другие узлы, то нельзя изменить его значение кнопкой 'Изменить значение'.\n"
            f"Невозможно добавить узел без открытого документа.\n"

        )
        messagebox.showinfo("Помощь", help_text)

    def on_info(self):
        info_text = (
            f"Редактор XML и JSON\n"
            f"Автор: Бабкин Денис Константинович\n"
            f"\n"
            f"Это приложение предназначено для работы с файлами в форматах XML и JSON. "
            f"Оно позволяет загружать, редактировать и сохранять данные, "
            f"отображая их в древовидной структуре. "
            f"Приложение поддерживает добавление, удаление и изменение узлов, "
            f"валидацию данных с использованием JSON Schema и XSD, "
            f"а также цветовое кодирование различных типов элементов."
        )
        messagebox.showinfo("О программе", info_text)

    def on_validate(self, target):
        self.controller.validate(target)

    def on_double_click(self, event):
        self.controller.edit_node_value()

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
        dialog.geometry("300x300")

        # Доступные типы для JSON и XML
        if self.current_file_type == "json":
            types = [
                ("Object", "dict"),
                ("List", "list"),
                ("Number", "number"),
                ("String", "string"),
                ("Bool", "boolean"),
                ("Null", "null")
            ]
        elif self.current_file_type == "xml":
            types = [
                ("Node", "node"),
                ("Attribute", "attribute"),
                ("Commentary", "comment"),
                # ("Инструкция обработки", "pi"),
            ]

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

        # Для XML: скрываем поле значения для узла или инструкции обработки
        if self.current_file_type == "xml" and node_type in ["node", "pi"]:
            value_entry.grid_remove()
        # Для XML: скрываем поле значения для узла или инструкции обработки
        if self.current_file_type == "xml" and node_type in ["text", "comment"]:
            key_entry.grid_remove()

        # Для JSON: скрываем поле значения для списка, словаря и null
        if self.current_file_type == "json" and node_type in ["dict", "list", "null"]:
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

    # Метод для изменения узла
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
        expansion_state = self.save_expansion_state()

        self.tree.delete(*self.tree.get_children())

        self._populate_tree_recursive("", data)

        self.restore_expansion_state(expansion_state)

    def _populate_tree_recursive(self, parent, data):
        match self.current_file_type:
            case "xml":
                if isinstance(data, dict):
                    for key, value in data.items():
                        key_without_num = ''

                        key_split = key.split("_")
                        if len(key_split) > 1:
                            if key_split[-1].isdigit():
                                key_without_num = "_".join(key_split[:-1])

                        if key.startswith('@'):
                            # Атрибуты
                            display_key = key
                            display_value = value
                            self.tree.insert(parent, 'end', text=display_key, values=(display_value,),
                                             tags=('attribute', key))
                        elif '#comment' in key:
                            display_value = value
                            self.tree.insert(parent, 'end', text="#comment", values=(display_value,),
                                             tags=('comment', key))
                        # elif key == '#processing_instruction':
                        #     for pi in value:
                        #         self.tree.insert(parent, 'end', text="#processing_instruction", values=(pi,),
                        #                          tags=('processing_instruction',))
                        elif key == '#text':
                            # TODO: тут можно родителю текст давать
                            self.tree.item(parent, values=(value,))
                            self.tree.insert(parent, 'end', text="#text", values=(value,), tags=('text', key))
                        elif isinstance(value, dict):
                            # TODO: кринж если он сделает abcd_1234
                            if key_without_num != '':
                                node = self.tree.insert(parent, 'end', text=key_without_num, values=("",),
                                                        tags=('node', key))
                                self._populate_tree_recursive(node, value)
                            else:
                                node = self.tree.insert(parent, 'end', text=key, values=("",),
                                                        tags=('node', key))
                                self._populate_tree_recursive(node, value)
                        else:
                            if key_without_num != '':
                                self.tree.insert(parent, 'end', text=key_without_num, values=(value,),
                                                 tags=('node', key))
                            else:
                                self.tree.insert(parent, 'end', text=key, values=(value,), tags=('node', key))
                else:
                    self.tree.insert(parent, 'end', text="Value", values=(data,), tags=('value',))
            case "json":
                if isinstance(data, dict):
                    for key, value in data.items():
                        tag = self.get_json_type_tag(value)
                        node = self.tree.insert(parent, 'end', text=key, values=(str(value),), tags=(tag, key,))
                        if isinstance(value, list) or isinstance(value, dict):
                            self._populate_tree_recursive(node, value)
                elif isinstance(data, list):
                    for index, item in enumerate(data):
                        tag = self.get_json_type_tag(item)
                        node = self.tree.insert(parent, 'end', text=f"[{index}]", values=(item, index,),
                                                tags=(tag, 'list_el',))
                        if isinstance(item, list) or isinstance(item, dict):
                            self._populate_tree_recursive(node, item)
                else:
                    self.get_json_type_tag(data)
                    self.tree.insert(parent, 'end', text="Value", values=(data,), tags=('value',))
        self.apply_tags_colors()

    def save_expansion_state(self):
        """Сохраняет состояние открытости всех узлов дерева по пути от корня."""
        state = {}
        for item in self.tree.get_children(''):
            self._save_expansion_state_recursive(item, state, [])
        return state

    def _save_expansion_state_recursive(self, item, state, path):
        # Добавляем текущий узел в путь
        current_path = path + [self.tree.item(item, 'tags')[1]]
        # Сохраняем состояние открытости узла
        state[tuple(current_path)] = self.tree.item(item, 'open')
        # Рекурсивно проходим по дочерним элементам
        for child in self.tree.get_children(item):
            self._save_expansion_state_recursive(child, state, current_path)

    def restore_expansion_state(self, state):
        """Восстанавливает состояние открытости всех узлов дерева по пути."""

        def find_node_by_path(current_item, current_path):
            for child in self.tree.get_children(current_item):
                if self.tree.item(child, 'tags')[1] == current_path[0]:
                    if len(current_path) == 1:
                        return child
                    return find_node_by_path(child, current_path[1:])
            return None

        for path, is_open in state.items():
            node = find_node_by_path('', list(path))
            if node:
                self.tree.item(node, open=is_open)

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
            return 'dict'
        elif isinstance(value, list):
            return 'list'
        else:
            return 'unknown'

    def convert_by_type_tags(self, tags, value):
        for tag in tags:
            if tag in ('string', 'boolean', 'null', 'number'):
                match tag:
                    case 'string':
                        return str(value)
                    case 'boolean':
                        return value.lower() == 'true'
                    case 'null':
                        return None
                    case 'number':
                        return int(value)
        return value

    def apply_tags_colors(self):
        self.tree.tag_configure('node', foreground='black')
        self.tree.tag_configure('attribute', foreground='firebrick')
        self.tree.tag_configure('comment', foreground='green')
        self.tree.tag_configure('processing_instruction', foreground='purple')
        self.tree.tag_configure('text', foreground='grey')
        self.tree.tag_configure('list', foreground='olive')
        self.tree.tag_configure('string', foreground='blue3')
        self.tree.tag_configure('number', foreground='chartreuse4')
        self.tree.tag_configure('boolean', foreground='dodgerblue3')
        self.tree.tag_configure('null', foreground='darkseagreen4', font=('TkDefaultFont', 10, 'italic'))
        self.tree.tag_configure('dict', foreground='teal')
        self.tree.tag_configure('list_el', foreground='orange')
        self.tree.tag_configure('unknown', foreground='black')

    def display_details(self, item):
        details = self.controller.get_node_details(item)

        self.details_entries["Ключ"].delete(0, tk.END)
        self.details_entries["Ключ"].insert(0, details["key"])

        self.details_entries["Значение"].delete(0, tk.END)
        self.details_entries["Значение"].insert(0, details["value"])

        self.type_dropdown['values'] = self.controller.get_available_types()
        self.type_var.set(details["type"])

        if details["change_key"]:
            self.buttons["edit_key_btn"].config(state="normal")
        else:
            self.buttons["edit_key_btn"].config(state="disabled")

        if details["change_val"]:
            self.buttons["edit_val_btn"].config(state="normal")
        else:
            self.buttons["edit_val_btn"].config(state="disabled")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def prompt_user(self, prompt, initialvalue=""):
        return simpledialog.askstring("Ввод", prompt, initialvalue=initialvalue)
