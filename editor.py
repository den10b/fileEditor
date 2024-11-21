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


class XMLEditor(BaseEditor):
    def load(self, filepath):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(filepath, parser)
        self.data = tree.getroot()

    def save(self, filepath):
        tree = etree.ElementTree(self.data)
        tree.write(filepath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def add_node(self, parent, node_name, text=None):
        new_element = etree.SubElement(parent, node_name)
        if text:
            new_element.text = text

    def delete_node(self, parent, child):
        parent.remove(child)


class JSONEditor(BaseEditor):
    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_node(self, parent, node_name, text=None):
        if isinstance(parent, dict):
            parent[node_name] = text if text else None
        elif isinstance(parent, list):
            parent.append(text if text else {})

    def delete_node(self, parent, child):
        if isinstance(parent, dict):
            parent.pop(child, None)
        elif isinstance(parent, list):
            try:
                parent.remove(child)
            except ValueError:
                pass
