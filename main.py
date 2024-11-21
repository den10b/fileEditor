# main.py
from tkinter import Tk
from ui import EditorUI

if __name__ == "__main__":
    root = Tk()
    app = EditorUI(root)
    root.geometry("1000x700")
    root.mainloop()




# import tkinter as tk
# from tkinter import filedialog, ttk, messagebox, simpledialog
# import xml.etree.ElementTree as ET
# import json
#
#
# class XMLJSONEditorApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("XML/JSON Editor")
#
#         # Панель инструментов
#         toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
#         tk.Button(toolbar, text="Добавить узел", command=self.add_node).pack(side=tk.LEFT, padx=2, pady=2)
#         tk.Button(toolbar, text="Удалить узел", command=self.delete_node).pack(side=tk.LEFT, padx=2, pady=2)
#         tk.Button(toolbar, text="Редактировать узел", command=self.edit_node).pack(side=tk.LEFT, padx=2, pady=2)
#         tk.Button(toolbar, text="Сохранить", command=self.save_file).pack(side=tk.LEFT, padx=2, pady=2)
#         toolbar.pack(side=tk.TOP, fill=tk.X)
#
#         # Основное окно
#         self.main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
#         self.main_frame.pack(fill=tk.BOTH, expand=True)
#
#         # Древовидная структура
#         self.tree_frame = tk.Frame(self.main_frame)
#         self.tree = ttk.Treeview(self.tree_frame)
#         self.tree.pack(fill=tk.BOTH, expand=True)
#         self.tree.bind("<Double-1>", self.edit_node)  # Редактирование по двойному клику
#         self.main_frame.add(self.tree_frame)
#
#         # Текстовое поле
#         self.text_frame = tk.Frame(self.main_frame)
#         self.text_box = tk.Text(self.text_frame, wrap=tk.NONE)
#         self.text_box.pack(fill=tk.BOTH, expand=True)
#         self.text_box.bind("<FocusOut>", self.sync_from_text)  # Синхронизация при потере фокуса
#         self.main_frame.add(self.text_frame)
#
#         self.data = None
#         self.current_file = None
#         self.file_type = None
#
#     def open_file(self):
#         # Открыть XML/JSON файл
#         filepath = filedialog.askopenfilename(
#             title="Открыть файл",
#             filetypes=[("XML/JSON файлы", "*.xml *.json"), ("Все файлы", "*.*")]
#         )
#         if not filepath:
#             return
#         try:
#             if filepath.endswith(".xml"):
#                 tree = ET.parse(filepath)
#                 root = tree.getroot()
#                 self.current_file = filepath
#                 self.data = root
#                 self.file_type = "XML"
#                 self.display_tree(root)
#                 self.display_text(root)
#             elif filepath.endswith(".json"):
#                 with open(filepath, "r") as f:
#                     self.data = json.load(f)
#                 self.current_file = filepath
#                 self.file_type = "JSON"
#                 self.display_tree(self.data)
#                 self.display_text(self.data)
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
#
#     def save_file(self):
#         # Сохранить файл
#         if not self.current_file:
#             self.current_file = filedialog.asksaveasfilename(
#                 title="Сохранить файл",
#                 filetypes=[("XML/JSON файлы", "*.xml *.json")]
#             )
#         if not self.current_file:
#             return
#         try:
#             if self.file_type == "XML":
#                 with open(self.current_file, "w") as f:
#                     xml_string = ET.tostring(self.data, encoding="unicode")
#                     clean_xml = self.clean_xml_string(xml_string)
#                     f.write(clean_xml)
#             elif self.file_type == "JSON":
#                 with open(self.current_file, "w") as f:
#                     json.dump(self.data, f, indent=4)
#             messagebox.showinfo("Сохранение", "Файл успешно сохранён.")
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
#
#     def display_tree(self, element, parent=""):
#         # Сохранение состояния раскрытых узлов
#         expanded_nodes = self.get_expanded_nodes()
#         self.tree.delete(*self.tree.get_children())
#         if self.file_type == "XML":
#             root_id = self.tree.insert("", "end", text=element.tag)
#             self.populate_tree_xml(element, root_id)
#         elif self.file_type == "JSON":
#             self.populate_tree_json(element, "")
#
#         # Восстановление состояния раскрытых узлов
#         self.set_expanded_nodes(expanded_nodes)
#
#     def populate_tree_xml(self, element, parent):
#         # Рекурсивное заполнение дерева для XML
#         for child in element:
#             node_id = self.tree.insert(parent, "end", text=child.tag)
#             self.populate_tree_xml(child, node_id)
#         if element.text and element.text.strip():
#             self.tree.insert(parent, "end", text=element.text.strip())
#
#     def populate_tree_json(self, element, parent):
#         # Рекурсивное заполнение дерева для JSON
#         if isinstance(element, dict):
#             for key, value in element.items():
#                 node_id = self.tree.insert(parent, "end", text=key)
#                 self.populate_tree_json(value, node_id)
#         elif isinstance(element, list):
#             for i, value in enumerate(element):
#                 node_id = self.tree.insert(parent, "end", text=f"[{i}]")
#                 self.populate_tree_json(value, node_id)
#         else:
#             self.tree.insert(parent, "end", text=element)
#
#     def display_text(self, element):
#         # Показать данные в текстовом поле
#         if self.file_type == "XML":
#             xml_string = ET.tostring(element, encoding="unicode")
#             clean_xml = self.clean_xml_string(xml_string)
#             self.text_box.delete(1.0, tk.END)
#             self.text_box.insert(tk.END, clean_xml)
#         elif self.file_type == "JSON":
#             self.text_box.delete(1.0, tk.END)
#             self.text_box.insert(tk.END, json.dumps(element, indent=4))
#
#     def clean_xml_string(self, xml_string):
#         # Убираем лишние пустые строки
#         lines = xml_string.splitlines()
#         return "\n".join(line for line in lines if line.strip())
#
#     def get_expanded_nodes(self):
#         # Получить список раскрытых узлов
#         expanded = []
#         for node in self.tree.get_children():
#             expanded.extend(self._get_expanded_recursively(node))
#         return expanded
#
#     def _get_expanded_recursively(self, node):
#         nodes = [node] if self.tree.item(node, "open") else []
#         for child in self.tree.get_children(node):
#             nodes.extend(self._get_expanded_recursively(child))
#         return nodes
#
#     def set_expanded_nodes(self, expanded_nodes):
#         # Восстановить состояние раскрытых узлов
#         for node in expanded_nodes:
#             self.tree.item(node, open=True)
#
#     def sync_from_text(self, event=None):
#         # Синхронизация дерева из текстового поля
#         try:
#             raw_text = self.text_box.get(1.0, tk.END).strip()
#             if self.file_type == "XML":
#                 root = ET.fromstring(raw_text)
#                 self.data = root
#                 self.display_tree(root)
#             elif self.file_type == "JSON":
#                 self.data = json.loads(raw_text)
#                 self.display_tree(self.data)
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось синхронизировать текст: {e}")
#
#     def delete_node(self):
#         selected_item = self.tree.focus()
#         if not selected_item:
#             messagebox.showerror("Ошибка", "Выберите узел для удаления.")
#             return
#
#         parent_item = self.tree.parent(selected_item)
#
#         if self.file_type == "XML":
#             element_to_delete = self.get_element_from_tree(selected_item)
#
#     def add_node(self):
#         selected_item = self.tree.focus()
#         if not selected_item:
#             messagebox.showerror("Ошибка", "Выберите узел для добавления.")
#             return
#
#         new_node_name = simpledialog.askstring("Добавить узел", "Введите имя нового узла:")
#         if not new_node_name:
#             return
#
#         if self.file_type == "XML":
#             parent_element = self.get_element_from_tree(selected_item)
#             if parent_element is not None:
#                 ET.SubElement(parent_element, new_node_name)
#         elif self.file_type == "JSON":
#             parent_data = self.get_json_from_tree(selected_item)
#             if isinstance(parent_data, dict):
#                 parent_data[new_node_name] = None
#             elif isinstance(parent_data, list):
#                 parent_data.append({})
#
#         self.display_tree(self.data)
#         self.display_text(self.data)
#
#     def edit_node(self, event=None):
#         # Редактировать узел
#         selected_item = self.tree.focus()
#         if not selected_item:
#             return
#
#         current_value = self.tree.item(selected_item, "text")
#
#         # Используем Toplevel для редактирования текста
#         edit_window = tk.Toplevel(self.root)
#         edit_window.title("Редактировать узел")
#
#         tk.Label(edit_window, text="Введите новое значение:").pack(pady=5)
#
#         text_area = tk.Text(edit_window, wrap=tk.WORD, height=10, width=40)
#         text_area.insert(tk.END, current_value)
#         text_area.pack(pady=5)
#
#         def save_edit():
#             new_value = text_area.get(1.0, tk.END).strip()
#             if new_value:
#                 if self.file_type == "XML":
#                     element = self.get_element_from_tree(selected_item)
#                     if element is not None:
#                         element.text = new_value
#                 elif self.file_type == "JSON":
#                     parent_item = self.tree.parent(selected_item)
#                     parent_data = self.get_json_from_tree(parent_item)
#                     if isinstance(parent_data, list):
#                         index = int(current_value.strip("[]"))
#                         parent_data[index] = new_value
#                     else:
#                         parent_data[current_value] = new_value
#                 self.display_tree(self.data)
#                 self.display_text(self.data)
#             edit_window.destroy()
#
#         tk.Button(edit_window, text="Сохранить", command=save_edit).pack(pady=5)
#
#     def get_element_from_tree(self, tree_item):
#         # Получить элемент XML по элементу дерева
#         path = []
#         while tree_item:
#             path.insert(0, self.tree.item(tree_item, "text"))
#             tree_item = self.tree.parent(tree_item)
#
#         element = self.data
#         for tag in path:
#             element = next((child for child in element if child.tag == tag), None)
#             if element is None:
#                 break
#         return element
#
#     def get_json_from_tree(self, tree_item):
#         # Рекурсивно получить JSON данные по элементу дерева
#         path = []
#         while tree_item:
#             path.insert(0, self.tree.item(tree_item, "text"))
#             tree_item = self.tree.parent(tree_item)
#
#         current_data = self.data
#         for key in path:
#             if isinstance(current_data, dict):
#                 current_data = current_data[key]
#             elif isinstance(current_data, list):
#                 index = int(key.strip("[]"))
#                 current_data = current_data[index]
#         return current_data
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = XMLJSONEditorApp(root)
#     root.geometry("1000x700")
#
#     # Добавить меню
#     menubar = tk.Menu(root)
#     menubar.add_command(label="Открыть", command=app.open_file)
#     menubar.add_command(label="Сохранить", command=app.save_file)
#     root.config(menu=menubar)
#
#     root.mainloop()
