"""Визуализация графа зависимостей в формате D2 и в виде дерева."""

import json


def generate_d2(graph):
    """Создать D2-код: показать все узлы, включая изолированные, и связи."""
    if not isinstance(graph, dict):
        raise ValueError("Граф должен быть словарём")

    lines = []
    for package, dependencies in graph.items():
        lines.append(json.dumps(package, ensure_ascii=False))
        for dependency in dependencies:
            source = json.dumps(package, ensure_ascii=False)
            target = json.dumps(dependency, ensure_ascii=False)
            lines.append(f"{source} -> {target}")
    return "\n".join(lines)


def save_d2(graph, filename="graph.d2"):
    """Записать D2-код в UTF-8 файл и вернуть путь к нему."""
    d2_code = generate_d2(graph)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(d2_code)
    return filename


def _append_ascii_branches(graph, package, prefix, visited, lines):
    """Добавить ветви дерева, предотвращая зацикливание в текущем пути."""
    dependencies = graph.get(package, [])
    for index, dependency in enumerate(dependencies):
        is_last = index == len(dependencies) - 1
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + dependency)
        if dependency in visited:
            continue
        child_prefix = prefix + ("    " if is_last else "│   ")
        _append_ascii_branches(
            graph, dependency, child_prefix, visited | {dependency}, lines
        )


def generate_ascii_tree(graph, root):
    """Вернуть текстовое дерево зависимостей от указанного корня."""
    if root not in graph:
        raise ValueError("Указанный пакет отсутствует в графе")
    lines = [root]
    _append_ascii_branches(graph, root, "", {root}, lines)
    return "\n".join(lines)
