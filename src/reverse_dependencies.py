"""Поиск пакетов, зависящих от заданного пакета в графе."""


def _invert_graph(graph):
    """Развернуть направления рёбер исходного графа."""
    reverse_graph = {package: [] for package in graph}
    for package, dependencies in graph.items():
        for dependency in dependencies:
            reverse_graph.setdefault(dependency, [])
            if package not in reverse_graph[dependency]:
                reverse_graph[dependency].append(package)
    return reverse_graph


def _collect_dependents(reverse_graph, package_name):
    """Обойти обратный граф стеком, не посещая узлы повторно."""
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


def get_reverse_dependencies(graph, package_name):
    """Вернуть отсортированные прямые и косвенные обратные зависимости."""
    if not isinstance(graph, dict):
        raise ValueError("Граф должен быть словарем")
    if not package_name:
        raise ValueError("Название пакета не может быть пустым")
    if package_name not in graph:
        raise ValueError("Указанный пакет отсутствует в графе")
    return _collect_dependents(_invert_graph(graph), package_name)
