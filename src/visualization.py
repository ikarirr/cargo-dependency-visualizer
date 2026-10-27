import json

def generate_d2(graph):
    """
    Формирование текстового представления
    графа зависимостей на языке D2.
    """

    if not isinstance(graph, dict):
        raise ValueError("Граф должен быть словарём")

    lines = []

    for package, dependencies in graph.items():
        # Добавляем пакет, даже если у него нет зависимостей
        lines.append(
            f"{json.dumps(package, ensure_ascii=False)}"
        )

        for dependency in dependencies:
            # Создаём направленную связь между пакетами
            lines.append(
                f"{json.dumps(package, ensure_ascii=False)} -> "
                f"{json.dumps(dependency, ensure_ascii=False)}"
            )

    return "\n".join(lines)

def save_d2(graph, filename="graph.d2"):
    """
    Сохранение графа зависимостей в файл D2.
    """

    d2_code = generate_d2(graph)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(d2_code)

    return filename

def generate_ascii_tree(graph, root):
    """
    Создание ASCII-дерева зависимостей
    для выбранного пакета.
    """

    if root not in graph:
        raise ValueError("Указанный пакет отсутствует в графе")

    lines = [root]

    def build_tree(package, prefix, visited):
        dependencies = graph.get(package, [])

        for index, dependency in enumerate(dependencies):
            is_last = index == len(dependencies) - 1

            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + dependency)

            if dependency in visited:
                continue

            new_prefix = prefix + ("    " if is_last else "│   ")

            build_tree(
                dependency,
                new_prefix,
                visited | {dependency}
            )

    build_tree(root, "", {root})

    return "\n".join(lines)