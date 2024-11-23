# editor.py
from abc import ABC, abstractmethod
import json
from lxml import etree


class BaseEditor(ABC):
    def __init__(self):
        self.data = None

    @abstractmethod
    def load(self, filepath):
        pass

    @abstractmethod
    def save(self, filepath):
        pass

    @abstractmethod
    def add_node(self, parent, node_name, text=None):
        pass

    @abstractmethod
    def delete_node(self, parent, child):
        pass

    @abstractmethod
    def edit_node_name(self, node, new_name):
        pass

    @abstractmethod
    def edit_node_value(self, node, new_value):
        pass

    @abstractmethod
    def get_meta(self):
        pass


class XMLEditor(BaseEditor):
    def __init__(self):
        super().__init__()
        self.declaration = None  #

    def load(self, filepath):
        with open(filepath, "rb") as f:
            first_line = f.readline().strip()
            if b"<?xml" in first_line:
                self.declaration = first_line.decode("utf-8")
            # else:
            #     self.declaration = '<?xml version="1.0" encoding="UTF-8"?>'

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(filepath, parser)
        self.data = tree.getroot()

    def save(self, filepath):
        with open(filepath, "wb") as f:
            if self.declaration:
                f.write(self.declaration.encode("utf-8") + b"\n")
            tree = etree.ElementTree(self.data)
            tree.write(f, pretty_print=True, xml_declaration=False, encoding="UTF-8")

    def add_node(self, parent, node_name, text=None):
        new_element = etree.SubElement(parent, node_name)
        if text:
            new_element.text = text

    def delete_node(self, parent, child):
        parent.remove(child)

    def get_meta(self):
        return self.declaration

    def edit_node_name(self, node, new_name):
        if isinstance(node, etree._Element):
            node.tag = new_name

    def edit_node_value(self, node, new_value):
        if isinstance(node, etree._Element):
            node.text = new_value


class JSONNode:
    def __init__(self, key=None, value=None, parent=None):
        self.key = key
        self.value = value
        self.children = []
        self.parent = parent

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def remove_child(self, child_node):
        self.children.remove(child_node)

    def is_leaf(self):
        return not self.children

    def __repr__(self):
        return f"JSONNode(key={self.key}, value={self.value}, children={len(self.children)})"


class JSONWrapper:
    def __init__(self, json_data=None):
        self.root = JSONNode(key="root")
        if json_data:
            self._build_tree(json_data, self.root)

    def _build_tree(self, data, parent_node):
        if isinstance(data, dict):
            for key, value in data.items():
                child_node = JSONNode(key=key)
                parent_node.add_child(child_node)
                self._build_tree(value, child_node)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                child_node = JSONNode(key=f"[{index}]")
                parent_node.add_child(child_node)
                self._build_tree(value, child_node)
        else:
            parent_node.value = data

    def to_dict(self):
        return self._convert_to_dict(self.root)

    def _convert_to_dict(self, node):
        if node.is_leaf():
            return node.value
        if all(child.key.startswith("[") for child in node.children):
            return [self._convert_to_dict(child) for child in node.children]
        return {child.key: self._convert_to_dict(child) for child in node.children}

    def find_node(self, path):
        current_node = self.root
        for key in path:
            current_node = next(
                (child for child in current_node.children if child.key == key), None
            )
            if not current_node:
                return None
        return current_node


class JSONEditor(BaseEditor):
    def __init__(self):
        super().__init__()
        self.wrapper = None

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            self.wrapper = JSONWrapper(json_data)

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.wrapper.to_dict(), f, indent=4, ensure_ascii=False)

    def add_node(self, parent, node_name, text=None):
        path = self._get_path_from_node(parent)
        parent_node = self.wrapper.find_node(path)
        if not parent_node:
            raise KeyError("Parent node not found.")
        new_node = JSONNode(key=node_name, value=text)
        parent_node.add_child(new_node)

    def delete_node(self, parent, child):
        path = self._get_path_from_node(parent)
        parent_node = self.wrapper.find_node(path)
        if not parent_node:
            raise KeyError("Parent node not found.")
        child_node = next(
            (child for child in parent_node.children if child.key == child), None
        )
        if child_node:
            parent_node.remove_child(child_node)

    def edit_node_name(self, node, new_name):
        node.key = new_name

    def edit_node_value(self, node, new_value):
        node.value = new_value

    def get_meta(self):
        return None

    def _get_path_from_node(self, node):
        """Рекурсивно строит путь от узла до корня."""
        path = []
        current = node
        while current and current.key != "root":
            path.insert(0, current.key)
            current = current.parent
        return path