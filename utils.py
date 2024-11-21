# utils.py

def get_expanded_paths(tree):
    expanded_paths = []
    for node in tree.get_children():
        get_expanded_paths_recursively(tree, node, [], expanded_paths)
    return expanded_paths


def get_expanded_paths_recursively(tree, node, current_path, expanded_paths):
    node_text = tree.item(node, "text")
    new_path = current_path + [node_text]

    if tree.item(node, "open"):
        expanded_paths.append(new_path)
        for child in tree.get_children(node):
            get_expanded_paths_recursively(tree, child, new_path, expanded_paths)


def set_expanded_paths(tree, expanded_paths):
    for path in expanded_paths:
        node = find_node_by_path(tree, path)
        if node:
            tree.item(node, open=True)


def find_node_by_path(tree, path):
    parent = ''
    node = None
    for part in path:
        found = False
        for child in tree.get_children(parent):
            if tree.item(child, "text") == part:
                node = child
                parent = child
                found = True
                break
        if not found:
            return None
    return node
