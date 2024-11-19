# utils.py
def get_expanded_nodes(tree):
    expanded = []
    for node in tree.get_children():
        expanded.extend(_get_expanded_recursively(tree, node))
    return expanded


def _get_expanded_recursively(tree, node):
    nodes = [node] if tree.item(node, "open") else []
    for child in tree.get_children(node):
        nodes.extend(_get_expanded_recursively(tree, child))
    return nodes


def set_expanded_nodes(tree, expanded_nodes):
    for node in expanded_nodes:
        tree.item(node, open=True)
