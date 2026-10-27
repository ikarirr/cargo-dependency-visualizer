def get_reverse_dependencies(graph, package_name):
    """
    Получение обратных зависимостей пакета.

    Возвращает пакеты, которые прямо или косвенно
    зависят от указанного пакета.

    Используется обход графа без рекурсии.
    """

    if not isinstance(graph, dict):
        raise ValueError("Граф должен быть словарем")

    if not package_name:
        raise ValueError("Название пакета не может быть пустым")

    if package_name not in graph:
        raise ValueError("Указанный пакет отсутствует в графе")

    # Создаем обратный граф
    reverse_graph = {
        package: [] for package in graph
    }

    for package, dependencies in graph.items():
        for dependency in dependencies:
            reverse_graph.setdefault(dependency, [])

            if package not in reverse_graph[dependency]:
                reverse_graph[dependency].append(package)

    # Обход обратного графа с помощью стека
    visited = {package_name}
    stack = [package_name]
    result = []

    while stack:
        current_package = stack.pop()

        for dependent in reverse_graph[current_package]:
            if dependent not in visited:
                visited.add(dependent)
                result.append(dependent)
                stack.append(dependent)

    return sorted(result)