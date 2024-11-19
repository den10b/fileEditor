# editor.py
import xml.etree.ElementTree as ET
import json


class Editor:
    def __init__(self):
        self.data = None
        self.file_type = None

    def load_xml(self, filepath):
        tree = ET.parse(filepath)
        self.data = tree.getroot()
        self.file_type = "XML"

    def load_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.file_type = "JSON"

    def save_xml(self, filepath):
        tree = ET.ElementTree(self.data)
        tree.write(filepath, encoding="unicode", xml_declaration=True)

    def save_json(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_node(self, parent, node_name):
        if self.file_type == "XML":
            ET.SubElement(parent, node_name)
        elif self.file_type == "JSON":
            if isinstance(parent, dict):
                parent[node_name] = None
            elif isinstance(parent, list):
                parent.append({node_name: None})

    def delete_node(self, parent, child):
        if self.file_type == "XML":
            parent.remove(child)
        elif self.file_type == "JSON":
            if isinstance(parent, dict):
                parent.pop(child, None)
            elif isinstance(parent, list):
                parent.remove(child)
