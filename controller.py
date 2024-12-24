# controller.py
from tkinter import filedialog, messagebox
import json
from model import DataModel
from view import View
from lxml import etree


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)

    # Открытие файла
    def open_file(self, file_type):
        filetypes = [("All Files", "*.*")]
        if file_type == "json":
            filetypes = [("JSON Files", "*.json"), ("All Files", "*.*")]
        elif file_type == "xml":
            filetypes = [("XML Files", "*.xml"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(
            filetypes=filetypes
        )
        if file_path:
            try:
                if file_type == "json":
                    self.model.load_json(file_path)
                    self.view.current_file_type = 'json'
                elif file_type == "xml":
                    self.model.load_xml(file_path)
                    self.view.current_file_type = 'xml'
                self.view.populate_tree(self.model.data)
                # self.view.show_message("Успех", f"Файл '{file_path}' успешно открыт.")
            except Exception as e:
                self.view.show_error("Ошибка", f"Не удалось открыть файл: {e}")

    def get_available_types(self):
        if self.model.data_type == "json":
            return ["String", "Number", "Boolean", "Null", "Object", "Array"]
        elif self.model.data_type == "xml":
            return ["Attribute",
                    "Comment",
                    "Processing Instruction",
                    # "Text",
                    "Node"]
        return []

    def format_value(self, value):
        if self.model.data_type == 'json':
            if isinstance(value, str):
                # return f"\"{value}\""
                return f"{value}"
            elif isinstance(value, bool):
                return str(value).lower()
            elif value is None:
                return "null"
            else:
                return str(value)
        elif self.model.data_type == 'xml':
            return str(value)

    def get_tag(self, value):
        if self.model.data_type == 'json':
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
        elif self.model.data_type == 'xml':
            return 'node'

    def get_node_details(self, item):
        key = self.view.tree.item(item, 'text')
        value = self.view.tree.item(item, 'values')[0]
        tags = self.view.tree.item(item, 'tags')

        if 'attribute' in tags:
            node_type = "Attribute"
        elif 'comment' in tags:
            node_type = "Comment"
        elif 'processing_instruction' in tags:
            node_type = "Processing Instruction"
        elif 'text' in tags:
            node_type = "Text"
        elif 'string' in tags:
            node_type = "String"
        elif 'number' in tags:
            node_type = "Number"
        elif 'boolean' in tags:
            node_type = "Boolean"
        elif 'null' in tags:
            node_type = "Null"
        elif 'object' in tags:
            node_type = "Object"
        elif 'array' in tags:
            node_type = "Array"
        else:
            node_type = "Node"

        return {"key": key, "value": value, "type": node_type}

    # Сохранение файла
    def save_file(self, as_new=False):
        if not self.model.file_path or as_new:
            if self.model.data_type == 'json':
                file_types = [("JSON Files", "*.json"), ("All Files", "*.*")]
                def_ext = ".json"
            elif self.model.data_type == 'xml':
                file_types = [("XML Files", "*.xml"), ("All Files", "*.*")]
                def_ext = ".xml"
            else:
                file_types = [("JSON Files", "*.json"), ("XML Files", "*.xml"), ("All Files", "*.*")]
                def_ext = ".json"
            file_path = filedialog.asksaveasfilename(
                defaultextension=def_ext,
                filetypes=file_types
            )
            if not file_path:
                return
            self.model.file_path = file_path
        try:
            if self.model.data_type == "json":
                self.model.save_json()
            elif self.model.data_type == "xml":
                self.model.save_xml()
            self.view.show_message("Успех", f"Файл '{self.model.file_path}' успешно сохранён.")
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось сохранить файл: {e}")

    # Добавление узла
    def add_node(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите родительский узел для добавления.")
            return
        path = self.get_path(selected_item[0])
        key = self.view.prompt_user("Введите ключ для нового узла:")
        if not key:
            return
        value = self.view.prompt_user("Введите значение для нового узла:")
        if value is None:
            return
        try:
            # Определяем тип узла
            node_type = 'node'
            if self.model.data_type == 'json':
                # В JSON узлы могут быть как объектами, так и значениями
                # Здесь предполагается, что добавляемый узел - объект или значение
                node_type = 'node'
            elif self.model.data_type == 'xml':
                # В XML добавляем как обычный узел
                node_type = 'node'
            self.model.add_node(path, key, value, node_type=node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", f"Узел '{key}' успешно добавлен.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось добавить узел: {e}")

    # Добавление атрибута
    def add_attribute(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите узел для добавления атрибута.")
            return
        path = self.get_path(selected_item[0])
        key = self.view.prompt_user("Введите имя атрибута (без '@'):")
        if not key:
            return
        value = self.view.prompt_user("Введите значение атрибута:")
        if value is None:
            return
        try:
            full_key = f"@{key}"
            self.model.add_node(path, full_key, value, node_type='attribute')
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", f"Атрибут '{full_key}' успешно добавлен.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось добавить атрибут: {e}")

    # Добавление комментария
    def add_comment(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите узел для добавления комментария.")
            return
        path = self.get_path(selected_item[0])
        comment = self.view.prompt_user("Введите комментарий:")
        if not comment:
            return
        try:
            self.model.add_node(path, None, comment, node_type='comment')
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Комментарий успешно добавлен.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось добавить комментарий: {e}")

    # Добавление инструкции обработки
    def add_processing_instruction(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите узел для добавления инструкции обработки.")
            return
        path = self.get_path(selected_item[0])
        pi = self.view.prompt_user("Введите инструкцию обработки (например, target data):")
        if not pi:
            return
        try:
            self.model.add_node(path, None, pi, node_type='processing_instruction')
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Инструкция обработки успешно добавлена.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось добавить инструкцию обработки: {e}")

    # Удаление узла
    def delete_node(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите узел для удаления.")
            return
        path = self.get_path(selected_item[0])
        key = self.view.tree.item(selected_item[0], 'text')
        # Определение типа узла по тегам
        tags = self.view.tree.item(selected_item[0], 'tags')
        if 'attribute' in tags:
            node_type = 'attribute'
            key = key  # Атрибут уже содержит '@'
        elif 'comment' in tags:
            node_type = 'comment'
            # Для комментариев ключ — индекс в списке
            key = self.view.tree.index(selected_item[0], parent=self.view.tree.parent(selected_item[0]))
        elif 'processing_instruction' in tags:
            node_type = 'processing_instruction'
            # Для инструкций обработки ключ — индекс в списке
            key = self.view.tree.index(selected_item[0], parent=self.view.tree.parent(selected_item[0]))
        elif 'list' in tags:
            node_type = 'list'
            try:
                key = int(key.strip('[]'))
            except ValueError:
                self.view.show_error("Ошибка", "Некорректный индекс элемента списка.")
                return
        elif 'text' in tags:
            node_type = 'value'
            key = '#text'
        else:
            node_type = 'node'
            # Для узлов в списках, например, [0], [1], и т.д.
            if key.startswith('[') and key.endswith(']'):
                node_type = 'list'
                try:
                    key = int(key.strip('[]'))
                except ValueError:
                    self.view.show_error("Ошибка", "Некорректный индекс элемента списка.")
                    return
        try:
            self.model.delete_node(path, key, node_type=node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Узел успешно удалён.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except TypeError as e:
            self.view.show_error("Ошибка", f"Не удалось удалить узел: {e}")
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось удалить узел: {e}")
    def update_node(self, path, key, value, node_type='node'):
        try:
            self.model.update_node(path, key, value, node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Узел успешно обновлен.")
        except KeyError as e:
            self.view.show_error("Ошибка обновления узла", str(e))
        except Exception as e:
            self.view.show_error("Неизвестная ошибка", str(e))

    def add_node_action(self, key, value, node_type):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите родительский узел для добавления.")
            return

        path = self.get_path_from_tree_item(selected_item[0])
        try:
            if node_type == "number":
                value = int(value)
            elif node_type == "boolean":
                value = value.lower() == "true"
            elif node_type == "null":
                value = None

            self.model.add_node(path, key, value, node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Узел успешно добавлен.")
        except Exception as e:
            self.view.show_error("Ошибка добавления узла", str(e))

    # Изменение узла
    def edit_node(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            self.view.show_error("Ошибка", "Выберите узел для изменения.")
            return
        item = selected_item[0]
        key = self.view.tree.item(item, 'text')
        value = self.view.tree.item(item, 'values')[0]
        tags = self.view.tree.item(item, 'tags')

        # Определение типа узла по тегам
        if 'attribute' in tags:
            node_type = 'attribute'
        elif 'comment' in tags:
            node_type = 'comment'
            # Для комментариев ключ — индекс
            key = self.view.tree.index(item, parent=self.view.tree.parent(item))
        elif 'processing_instruction' in tags:
            node_type = 'processing_instruction'
            # Для инструкций обработки ключ — индекс
            key = self.view.tree.index(item, parent=self.view.tree.parent(item))
        elif 'text' in tags:
            node_type = 'value'
            key = '#text'
        elif 'string' in tags or 'number' in tags or 'boolean' in tags or 'null' in tags:
            node_type = 'value'
            key = "Value"
        else:
            node_type = 'node'
            if key.startswith('[') and key.endswith(']'):
                node_type = 'list'
                try:
                    key = int(key.strip('[]'))
                except ValueError:
                    self.view.show_error("Ошибка", "Некорректный индекс элемента списка.")
                    return

        if node_type == 'value' and self.model.data_type == 'json':
            # Для JSON типов значений предоставляем выбор типа
            new_value = self.get_json_value()
            if new_value is None:
                return
        else:
            initial = value if node_type != 'value' else ''
            new_value = self.view.prompt_user("Введите новое значение:", initialvalue=initial)
            if new_value is None:
                return

        try:
            self.model.update_node(self.get_path(item), key, new_value, node_type=node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Узел успешно изменён.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except TypeError as e:
            self.view.show_error("Ошибка", f"Не удалось изменить узел: {e}")
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось изменить узел: {e}")

    # Получение значения с выбором типа для JSON
    def get_json_value(self):
        value = self.view.prompt_user("Введите значение:")
        if value is None:
            return None
        type_choice = self.view.prompt_user("Выберите тип значения (string, number, object, array, boolean, null):")
        if type_choice is None:
            return None
        type_choice = type_choice.lower()
        if type_choice == 'string':
            return value
        elif type_choice == 'number':
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                self.view.show_error("Ошибка", "Неверный формат числа.")
                return None
        elif type_choice == 'object':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                self.view.show_error("Ошибка", "Неверный формат объекта JSON.")
                return None
        elif type_choice == 'array':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                self.view.show_error("Ошибка", "Неверный формат массива JSON.")
                return None
        elif type_choice == 'boolean':
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            else:
                self.view.show_error("Ошибка", "Значение должно быть 'true' или 'false'.")
                return None
        elif type_choice == 'null':
            return None
        else:
            self.view.show_error("Ошибка", "Неверный тип значения.")
            return None

    # Валидация данных
    def validate(self, target):
        if target == "current":
            if not self.model.file_path:
                self.view.show_error("Ошибка", "Нет открытого файла для валидации.")
                return
            # Определение типов схемы в зависимости от файла
            if self.model.data_type == 'json':
                schema_filetypes = [("JSON Schema", "*.json"), ("All Files", "*.*")]
            elif self.model.data_type == 'xml':
                schema_filetypes = [("XML Schema", "*.xsd"), ("All Files", "*.*")]
            else:
                schema_filetypes = [("JSON Schema", "*.json"), ("XML Schema", "*.xsd"), ("All Files", "*.*")]
            schema_path = filedialog.askopenfilename(
                title="Выберите схему для валидации",
                filetypes=schema_filetypes
            )
            if not schema_path:
                return
            try:
                if self.model.data_type == "json":
                    with open(schema_path, 'r', encoding='utf-8') as file:
                        schema = json.load(file)
                    is_valid, message = self.model.validate_json(schema)
                elif self.model.data_type == "xml":
                    is_valid, message = self.model.validate_xml(schema_path)
                else:
                    self.view.show_error("Ошибка", "Не поддерживаемый тип данных.")
                    return
                if is_valid:
                    self.view.show_message("Валидация", message)
                else:
                    self.view.show_error("Валидация", message)
            except Exception as e:
                self.view.show_error("Ошибка", f"Не удалось выполнить валидацию: {e}")
        elif target == "other":
            # Приоритет типов файлов в зависимости от открытого файла
            if self.model.data_type == 'json':
                file_types = [("JSON Files", "*.json"), ("XML Files", "*.xml"), ("All Files", "*.*")]
            elif self.model.data_type == 'xml':
                file_types = [("XML Files", "*.xml"), ("JSON Files", "*.json"), ("All Files", "*.*")]
            else:
                file_types = [("JSON Files", "*.json"), ("XML Files", "*.xml"), ("All Files", "*.*")]
            file_path = filedialog.askopenfilename(
                title="Выберите файл для валидации",
                filetypes=file_types
            )
            if not file_path:
                return
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    # Выбор схемы JSON
                    schema_path = filedialog.askopenfilename(
                        title="Выберите JSON Schema",
                        filetypes=[("JSON Schema", "*.json"), ("All Files", "*.*")]
                    )
                    if not schema_path:
                        return
                    with open(schema_path, 'r', encoding='utf-8') as file:
                        schema = json.load(file)
                    is_valid, message = self.model.validate_json(schema)
                    if is_valid:
                        self.view.show_message("Валидация", "JSON файл валиден.")
                    else:
                        self.view.show_error("Валидация", message)
                elif file_path.endswith('.xml'):
                    # Выбор схемы XML
                    schema_path = filedialog.askopenfilename(
                        title="Выберите XML Schema",
                        filetypes=[("XML Schema", "*.xsd"), ("All Files", "*.*")]
                    )
                    if not schema_path:
                        return
                    temp_model = DataModel()
                    temp_model.load_xml(file_path)
                    is_valid, message = temp_model.validate_xml(schema_path)
                    if is_valid:
                        self.view.show_message("Валидация", "XML файл валиден.")
                    else:
                        self.view.show_error("Валидация", message)
                else:
                    self.view.show_error("Ошибка", "Неподдерживаемый формат файла для валидации.")
                    return
            except Exception as e:
                self.view.show_error("Валидация", f"Файл не валиден: {e}")

    def edit_xml_declaration(self):
        version = self.view.prompt_user("Введите версию XML:",
                                        initialvalue=self.model.xml_declaration.get("version", "1.0"))
        encoding = self.view.prompt_user("Введите кодировку XML:",
                                         initialvalue=self.model.xml_declaration.get("encoding", "UTF-8"))
        standalone = self.view.prompt_user("Введите значение standalone (yes/no, оставьте пустым для None):",
                                           initialvalue=self.model.xml_declaration.get("standalone", ""))
        standalone = standalone if standalone in ["yes", "no"] else None

        self.model.xml_declaration = {"version": version, "encoding": encoding, "standalone": standalone}
        self.view.show_message("Успех", "XML декларация обновлена.")

    # Получение пути к выбранному узлу
    def get_path(self, item):
        path = []
        while item:
            parent = self.view.tree.parent(item)
            text = self.view.tree.item(item, 'text')
            tags = self.view.tree.item(item, 'tags')
            # Обработка специальных узлов
            if text.startswith('@'):
                key = text
                path.insert(0, key)
            elif text == "#comment":
                key = '#comment'
                path.insert(0, key)
            elif text == "#processing_instruction":
                key = '#processing_instruction'
                path.insert(0, key)
            elif text == "#text":
                key = '#text'
                path.insert(0, key)
            elif text.startswith('[') and text.endswith(']'):
                # Список
                try:
                    index = int(text.strip('[]'))
                    path.insert(0, index)
                except ValueError:
                    # Некорректный индекс
                    path.insert(0, text)
            else:
                key = text
                path.insert(0, key)
            item = parent
        return path

    # Отображение деталей выбранного узла
    def display_details(self, item):
        self.view.display_details(item)

    # Обновление деталей узла
    def update_details(self, item, key, value, type_):
        path = self.get_path(item)
        node_type = type_
        if node_type == "Attribute":
            node_type = 'attribute'
        elif node_type == "Comment":
            node_type = 'comment'
            # Для комментариев ключ — индекс
            key = self.view.tree.index(item, parent=self.view.tree.parent(item))
        elif node_type == "Processing Instruction":
            node_type = 'processing_instruction'
            # Для инструкций обработки ключ — индекс
            key = self.view.tree.index(item, parent=self.view.tree.parent(item))
        elif node_type == "Text":
            node_type = 'value'
            key = '#text'
        elif node_type in ["String", "Number", "Boolean", "Null"]:
            node_type = 'value'
            key = "Value"
        elif node_type == "List":
            node_type = 'list'
            try:
                key = int(key.strip('[]'))
            except ValueError:
                self.view.show_error("Ошибка", "Некорректный индекс элемента списка.")
                return
        else:
            node_type = 'node'

        try:
            self.model.update_node(path, key, value, node_type=node_type)
            self.view.populate_tree(self.model.data)
            self.view.show_message("Успех", "Изменения успешно сохранены.")
        except KeyError as e:
            self.view.show_error("Ошибка", str(e))
        except TypeError as e:
            self.view.show_error("Ошибка", f"Не удалось сохранить изменения: {e}")
        except Exception as e:
            self.view.show_error("Ошибка", f"Не удалось сохранить изменения: {e}")

    def get_path_from_tree_item(self, item):
        path = []
        while item:
            parent = self.view.tree.parent(item)
            text = self.view.tree.item(item, "text")

            # Если текст узла - индекс списка ([0], [1], ...), преобразуем в число
            if text.startswith("[") and text.endswith("]"):
                path.insert(0, int(text[1:-1]))
            else:
                path.insert(0, text)

            item = parent
        return path


