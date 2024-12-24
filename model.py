# model.py
import json
from jsonschema import validate, ValidationError
from lxml import etree
import copy


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
        etree_dict = {element.tag: {} if element.attrib else None}
        # Обработка атрибутов
        if element.attrib:
            etree_dict[element.tag].update({
                f"@{k}": v for k, v in element.attrib.items()
                })
        # Обработка комментариев и инструкций обработки
        for child in element:
            if isinstance(child, etree._Comment):
                i=0
                while f'#comment_{i}' in etree_dict[element.tag]:
                    i+=1
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
                    # if not isinstance(etree_dict[element.tag][k], list):
                    #     etree_dict[element.tag][k] = [etree_dict[element.tag][k]]
                    # etree_dict[element.tag][k].append(v)
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
        assert isinstance(d, dict) and len(d) == 1
        tag, body = next(iter(d.items()))
        element = etree.Element(tag)
        self._dict_to_etree_recursive(element, body)
        return element

    def _dict_to_etree_recursive(self, parent, body):
        if isinstance(body, dict):
            for key, value in body.items():
                if key.startswith('@'):
                    parent.set(key[1:], value)
                elif key == '#text':
                    parent.text = value
                elif key == '#comment':
                    for comment in value:
                        comment_element = etree.Comment(comment)
                        parent.append(comment_element)
                elif key == '#processing_instruction':
                    for pi in value:
                        target, text = self._parse_processing_instruction(pi)
                        pi_element = etree.ProcessingInstruction(target, text)
                        parent.append(pi_element)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            child = etree.SubElement(parent, key)
                            self._dict_to_etree_recursive(child, item)
                        else:
                            # Примитивные типы в списках
                            child = etree.SubElement(parent, key)
                            child.text = str(item)
                else:
                    # Узлы с непосредственным значением
                    child = etree.SubElement(parent, key)
                    self._dict_to_etree_recursive(child, value)
        elif isinstance(body, list):
            for item in body:
                child = etree.SubElement(parent, parent.tag)
                self._dict_to_etree_recursive(child, item)
        else:
            # Для JSON типов значений
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
            if node_type == "attribute":
                if not isinstance(d, dict):
                    raise TypeError("Атрибуты могут быть добавлены только к объектам.")
                d[f"@{key}"] = value
            elif node_type == "comment":
                if "#comment" not in d:
                    d["#comment"] = []
                d["#comment"].append(value)
            elif node_type == "pi":
                if "#processing_instruction" not in d:
                    d["#processing_instruction"] = []
                d["#processing_instruction"].append(value)
            elif node_type == "list":
                if key not in d:
                    d[key] = []
                elif not isinstance(d[key], list):
                    raise TypeError("Ключ уже существует и не является списком.")
                d[key].append(value)
            else:
                d[key] = value
        except KeyError:
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Удаление узла
    def delete_node(self, path, key, node_type='node'):
        d = self.data
        try:
            for p in path:
                d = d[p]
            if node_type == 'attribute':
                del d[key]
            elif node_type == 'comment':
                if '#comment' in d and isinstance(d['#comment'], list) and 0 <= key < len(d['#comment']):
                    d['#comment'].pop(key)
                else:
                    raise KeyError("Комментарий не найден.")
            elif node_type == 'processing_instruction':
                if '#processing_instruction' in d and isinstance(d['#processing_instruction'], list) and 0 <= key < len(
                        d['#processing_instruction']):
                    d['#processing_instruction'].pop(key)
                else:
                    raise KeyError("Инструкция обработки не найдена.")
            elif node_type == 'list':
                if isinstance(d, list) and 0 <= key < len(d):
                    d.pop(key)
                else:
                    raise KeyError("Элемент списка не найден.")
            elif node_type == 'value':
                if key in d:
                    del d[key]
                else:
                    raise KeyError(f"Ключ '{key}' не найден.")
            else:
                if key in d:
                    del d[key]
                else:
                    raise KeyError(f"Ключ '{key}' не найден.")
        except (KeyError, TypeError):
            raise KeyError(f"Ключ '{key}' не найден по пути {'->'.join(map(str, path))}.")

    # Обновление узла
    def update_node(self, path, key, value, node_type='node'):
        d = self.data
        try:
            # Перемещаемся по пути до узла
            for p in path[:-1]:
                d = d[p]

            # Обновляем значение узла
            if isinstance(d, list):
                index = path[-1]
                if not isinstance(index, int) or not (0 <= index < len(d)):
                    raise KeyError(f"Индекс {index} вне диапазона списка.")
                d[index] = value
            else:
                if key in d:
                    d[key] = value
                else:
                    raise KeyError(f"Ключ '{key}' не найден.")
        except (KeyError, IndexError):
            raise KeyError(f"Путь {'->'.join(map(str, path))} не существует.")

    # Валидация JSON
    def validate_json(self, schema):
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
