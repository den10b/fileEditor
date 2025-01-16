# model.py
import json
from jsonschema import validate, ValidationError
from lxml import etree
import copy
import re


class DataModel:
    def __init__(self):
        self.data = {}
        self.file_path = None
        self.data_type = None  # 'json' или 'xml'
        self.xml_declaration = {"version": "1.0", "encoding": "UTF-8", "standalone": None}

    # Загрузка JSON файла
    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.file_path = file_path
        self.data_type = 'json'

    def _get_xml_declaration(self, file_path):
        # Чтение первой строки файла для декларации
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            if first_line.startswith("<?xml"):
                declaration = {}
                for attr in first_line[5:-2].split():
                    key, value = attr.split('=')
                    declaration[key] = value.strip('"')
                return declaration
        return {"version": "1.0", "encoding": "UTF-8", "standalone": None}

    # Загрузка XML файла
    def load_xml(self, file_path):
        tree = etree.parse(file_path)
        declaration = self._get_xml_declaration(file_path)
        if declaration:
            self.xml_declaration = declaration
        self.data = self._etree_to_dict(tree.getroot())
        self.file_path = file_path
        self.data_type = 'xml'

    # Преобразование XML в словарь
    def _etree_to_dict(self, element):
        etree_dict = {element.tag: {}}
        # Обработка атрибутов
        if element.attrib:
            etree_dict[element.tag].update({
                f"@{k}": v for k, v in element.attrib.items()
            })

        # Обработка комментариев и инструкций обработки
        for child in element:
            if isinstance(child, etree._Comment):
                i = 0
                while f'#comment_{i}' in etree_dict[element.tag]:
                    i += 1
                etree_dict[element.tag][f'#comment_{i}'] = child.text
                # if '#comment' not in etree_dict[element.tag]:
                #     etree_dict[element.tag]['#comment'] = []
                # etree_dict[element.tag]['#comment'].append(child.text)
                continue
            if isinstance(child, etree._ProcessingInstruction):
                # TODO: processing_instruction
                # pi = f"{child.target} {child.text}"
                # if '#processing_instruction' not in etree_dict[element.tag]:
                #     etree_dict[element.tag]['#processing_instruction'] = []
                # etree_dict[element.tag]['#processing_instruction'].append(pi)
                continue
            # Рекурсивная обработка дочерних элементов
            child_dict = self._etree_to_dict(child)
            for k, v in child_dict.items():
                if k in etree_dict[element.tag]:
                    i = 0
                    while f'{k}_{i}' in etree_dict[element.tag]:
                        i += 1
                    etree_dict[element.tag][f'{k}_{i}'] = v
                else:
                    etree_dict[element.tag][k] = v
        # Обработка текстового содержимого
        text = element.text.strip() if element.text else ''
        if text:
            etree_dict[element.tag] = {'#text': text}
        # if text and (len(element) == 0 and not element.attrib):
        #     etree_dict[element.tag] = text
        # elif text:
        #     etree_dict[element.tag]['#text'] = text
        return etree_dict

    # Сохранение JSON файла
    def save_json(self, file_path=None):
        if file_path:
            self.file_path = file_path
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    # Сохранение XML файла
    def save_xml(self, file_path=None):
        if file_path:
            self.file_path = file_path
        root = self._dict_to_etree(copy.deepcopy(self.data))
        tree = etree.ElementTree(root)
        tree.write(self.file_path, pretty_print=True, xml_declaration=True,
                   encoding=self.xml_declaration.get("encoding", "UTF-8"))

    # Преобразование словаря в XML
    def _dict_to_etree(self, d):
        # TODO: вот тут конечно недоделал (((
        assert isinstance(d, dict) and len(d) == 1
        tag, body = next(iter(d.items()))
        element = etree.Element(tag)
        self._dict_to_etree_recursive(element, body)
        return element

    def _dict_to_etree_recursive(self, parent, body):
        if isinstance(body, dict):
            for key, value in body.items():

                key_without_num = ''

                key_split = key.split("_")
                if len(key_split) > 1:
                    if key_split[-1].isdigit():
                        key_without_num = "_".join(key_split[:-1])
                else:
                    key_without_num = key
                if key.startswith('@'):
                    parent.set(key[1:], value)
                elif key == '#text':
                    parent.text = value
                elif '#comment' in key:
                    comment_element = etree.Comment(value)
                    parent.append(comment_element)
                # elif key == '#processing_instruction':
                #     for pi in value:
                #         target, text = self._parse_processing_instruction(pi)
                #         pi_element = etree.ProcessingInstruction(target, text)
                #         parent.append(pi_element)
                # elif isinstance(value, list):
                #     for item in value:
                #         if isinstance(item, dict):
                #             child = etree.SubElement(parent, key)
                #             self._dict_to_etree_recursive(child, item)
                #         else:
                #             # Примитивные типы в списках
                #             child = etree.SubElement(parent, key)
                #             child.text = str(item)
                else:
                    child = etree.SubElement(parent, key_without_num)
                    # TODO: сейчас проблема если будет узел формата abcd_0 или node_99
                    # if key_without_num in body:
                    #     child = etree.SubElement(parent, key_without_num)
                    # else:
                    #     child = etree.SubElement(parent, key)
                    self._dict_to_etree_recursive(child, value)
        # elif isinstance(body, list):
        #     for item in body:
        #         child = etree.SubElement(parent, parent.tag)
        #         self._dict_to_etree_recursive(child, item)
        else:
            parent.text = str(body)

    def _parse_processing_instruction(self, pi):
        parts = pi.split(' ', 1)
        target = parts[0].strip('?')
        text = parts[1].strip('?') if len(parts) > 1 else ''
        return target, text

    # Добавление узла
    def add_node(self, path, key, value, node_type='node'):
        d = self.data
        try:
            for p in path:
                d = d[p]
            if self.data_type == "json":
                if isinstance(d, dict):
                    if key in d:
                        raise KeyError(f"Элемент с ключом {key} уже существует.")
            if self.data_type == "xml":
                if isinstance(d, dict):
                    if "#text" in d:
                        if node_type != "attribute":
                            raise TypeError(f"Нельзя добавить узел к элементу, у которого есть текст.")
            match node_type:
                case "attribute":
                    if not isinstance(d, dict):
                        raise TypeError("Атрибуты могут быть добавлены только к объектам.")
                    if f"@{key}" in d:
                        raise KeyError(f"Атрибут {key} уже существует.")
                    d[f"@{key}"] = value
                case "comment":
                    if "#comment" in d:
                        i = 0
                        while f'#comment_{i}' in d:
                            i += 1
                        d[f'#comment_{i}'] = value
                    else:
                        d["#comment"] = value
                # elif node_type == "pi":
                #     if "#processing_instruction" not in d:
                #         d["#processing_instruction"] = []
                #     d["#processing_instruction"].append(value)
                case "list":
                    if isinstance(d, list):
                        d.append([])
                    else:
                        d[key] = []
                case "dict":
                    if isinstance(d, list):
                        d.append({})
                    else:
                        d[key] = {}
                case "node":
                    d[key] = {}
                # case "list_el":
                #     if not isinstance(d, list):
                #         raise TypeError("Родитель - не список.")
                #     d.append(value)
                case _:
                    match self.data_type:
                        case "json":
                            if isinstance(d, list):
                                d.append(value)
                            else:
                                d[key] = value
                        case "xml":
                            if key in d:
                                i = 0
                                while f'{key}_{i}' in d:
                                    i += 1
                                d[f'{key}_{i}'] = value
                            else:
                                d[key] = value
        except KeyError:
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Удаление узла
    def delete_node(self, path, key, node_type='node'):
        d = self.data
        try:
            for p in path[:-1]:
                d = d[p]
            # d это родитель ( по-идее )
            if key != path[-1]:
                raise KeyError(f"Элемент '{key}' отсутствует по пути {'->'.join(map(str, path))}.")
            if isinstance(d, list):
                if len(d) <= key:
                    raise KeyError(f"В списке нет элемента '{key}'.")
                d.pop(key)
            elif isinstance(d, dict):
                if key not in d:
                    raise KeyError(f"Ключ '{key}' не найден.")
                del d[key]
            else:
                raise KeyError(f"Ключ '{key}' ни в словаре, ни в списке.")

        except (KeyError, TypeError):
            raise KeyError(f"Ключ '{key}' не найден по пути {'->'.join(map(str, path))}.")

    # Обновление узла
    def update_node_key(self, path, new_key):
        d = self.data
        try:
            # Перемещаемся по пути до узла
            for p in path[:-1]:
                d = d[p]
            # d это родитель
            old_key = path[-1]
            if old_key == new_key:
                print("Узел не меняется.")
                return
            if old_key.startswith('@'):
                new_key = f'@{new_key}'
                # Обновляем значение узла
            if isinstance(d, list):
                raise KeyError(f"Индекс в спискe изменить нельзя.")
            if isinstance(d, dict):
                match self.data_type:
                    case "json":
                        if new_key in d:
                            raise KeyError(f"Элемент {new_key} уже существует.")
                        d[new_key] = d[old_key]
                        del d[old_key]
                    case "xml":
                        if new_key in d:
                            i = 0
                            while f'{new_key}_{i}' in d:
                                i += 1
                            d[f'{new_key}_{i}'] = d[old_key]
                            del d[old_key]
                        else:
                            d[new_key] = d[old_key]
                            del d[old_key]
            else:
                raise KeyError(f"Родитель элемента '{old_key}' - не dict.")
        except (KeyError, IndexError):
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Обновление узла
    def update_node_value(self, path, new_value):
        d = self.data
        try:
            # Перемещаемся по пути до родителя узла
            for p in path[:-1]:
                d = d[p]
            # d это родитель
            key = path[-1]
            old_value = d[key]
            if old_value == new_value:
                print("Узел не меняется.")
                return
            if self.data_type == "xml":
                if isinstance(old_value, dict):
                    for child_key in old_value.keys():
                        if not (child_key == "#text" or child_key.startswith("@")):
                            raise TypeError(f"Нельзя добавлять текст к узлам, внутри которых есть другие узлы.")
                    old_value["#text"] = new_value
                    d[key] = old_value
                    return
            if key in d:
                d[key] = new_value
            else:
                raise KeyError(f"Ключ '{key}' не найден.")
        except (KeyError, IndexError):
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Обновление узла
    def update_node_type(self, path, new_type='node'):
        d = self.data
        try:
            # Перемещаемся по пути до родителя узла
            for p in path[-1]:
                d = d[p]
            # d это родитель

            key = path[-1]

            if key not in d:
                raise KeyError(f"Ключ '{key}' не найден.")
            match new_type:
                case "attribute":
                    if not isinstance(d, dict):
                        raise TypeError("Атрибуты могут быть добавлены только к объектам.")
                    if f"@{key}" in d:
                        raise KeyError(f"Атрибут {key} уже существует.")
                    d[f"@{key}"] = ""
                case "comment":
                    if "#comment" in d:
                        i = 0
                        while f'#comment_{i}' in d:
                            i += 1
                        d[f'#comment_{i}'] = ""
                    else:
                        d["#comment"] = ""
                # elif node_type == "pi":
                #     if "#processing_instruction" not in d:
                #         d["#processing_instruction"] = []
                #     d["#processing_instruction"].append(value)
                case "list":
                    d[key] = []
                case "dict":
                    d[key] = {}
                case "string":
                    d[key] = ""
                case "boolean":
                    d[key] = False
                case "null":
                    d[key] = None
                case "number":
                    d[key] = 0
                case "unknown":
                    d[key] = None
                case _:
                    raise TypeError(f"Неизвестный тип данных.")
        except (KeyError, IndexError):
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Валидация JSON
    def validate_json(self, schema):
        try:
            validate(instance=self.data, schema=schema)
            return True, "JSON валиден."
        except ValidationError as e:
            return False, f"Ошибка валидации: {e.message}"

    def validate_new_json(self, schema):
        try:
            validate(instance=self.data, schema=schema)
            return True, "JSON валиден."
        except ValidationError as e:
            return False, f"Ошибка валидации: {e.message}"

    # Валидация XML
    def validate_xml(self, schema_path):
        xmlschema_doc = etree.parse(schema_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        root = self._dict_to_etree(copy.deepcopy(self.data))
        try:
            xmlschema.assertValid(root)
            return True, "XML валиден."
        except etree.DocumentInvalid as e:
            return False, f"Ошибка валидации: {e.error_log}"

    def xml_have_child_nodes(self, path):
        d = self.data
        try:
            # Перемещаемся по пути до родителя узла
            for p in path:
                d = d[p]
            if self.data_type == "xml":
                if isinstance(d, dict):
                    for child_key in d.keys():
                        if not (child_key == "#text" or child_key.startswith("@")):
                            return True
            return False
        except:
            raise Exception("Ошибка!")

    def validate_new_xml(self, schema_path):
        xmlschema_doc = etree.parse(schema_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        root = self._dict_to_etree(copy.deepcopy(self.data))
        try:
            xmlschema.assertValid(root)
            return True, "XML валиден."
        except etree.DocumentInvalid as e:
            return False, f"Ошибка валидации: {e.error_log}"

    def validate_all_pass(self):
        if isinstance(self.data, dict):
            try:
                self.validate_all_pass_recursive(self.data,"")
                return
            except Exception as e:
                raise Exception(f"{e}")

    def validate_all_pass_recursive(self, body, path):
        if isinstance(body, dict):
            for key, value in body.items():
                if re.search('pass|key|пароль|ключ', key) is not None:
                    if isinstance(value, str):
                        try:
                            validate_pass(value)
                        except Exception as e:
                            raise Exception(f"Ошибка проверки пароля по пути {path} > {key}:\n"
                                            f"{e}")
                if isinstance(value, dict) or isinstance(value, list):
                    self.validate_all_pass_recursive(value, f"{path} > {key}")
        elif isinstance(body, list):
            for key, value in enumerate(body):
                if isinstance(value, dict) or isinstance(value, list):
                    self.validate_all_pass_recursive(value, f"{path} > {key}")

def validate_pass(password):
    if len(password) < 8:
        raise Exception("Пароль короче 8 символов")
    elif re.search('[0-9]', password) is None:
        raise Exception("В пароле нет цифр")
    elif re.search('[A-Z]|[А-Я]', password) is None:
        raise Exception("В пароле нет заглавных букв")
    elif re.search('[a-z]|[А-Я]', password) is None:
        raise Exception("В пароле нет строчных букв")
    elif re.search('[@$!%*#?&]', password) is None:
        raise Exception("В пароле нет спецсимволов")
    else:
        return
