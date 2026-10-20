from collections import deque

from src.dependencies import get_dependencies, get_latest_version

def build_graph(
    package_name,
    package_version,
    repository_url,
    max_depth,
    dependency_provider=None
):
    """
    Построение графа зависимостей Cargo.

    Используется алгоритм DFS без рекурсии.
    Обход выполняется с помощью стека.

    Args:
        package_name: название исходного пакета.
        package_version: версия исходного пакета.
        repository_url: адрес репозитория.
        max_depth: максимальная глубина обхода.
        dependency_provider: функция получения зависимостей.

    Returns:
        dict: граф зависимостей.
    """

    if not package_name:
        raise ValueError("Название пакета не может быть пустым")

    if not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError("Глубина должна быть неотрицательным числом")

    if dependency_provider is None:
        dependency_provider = get_dependencies

    graph = {}
    visited = set()

    # Стек для обхода графа в глубину
    stack = deque([
        (package_name, package_version, 0)
    ])

    while stack:

        # DFS: извлекаем последний добавленный элемент
        current_package, current_version, depth = stack.pop()

        if current_package in visited:
            continue

        visited.add(current_package)

        graph.setdefault(current_package, [])

        # Проверяем ограничение глубины
        if depth >= max_depth:
            continue

        # Определяем версию пакета
        if current_version is None:
            current_version = get_latest_version(
                current_package,
                repository_url
            )

        # Получаем зависимости
        dependencies = dependency_provider(
            current_package,
            current_version,
            repository_url
        )

        for dependency in dependencies:

            if dependency not in graph[current_package]:
                graph[current_package].append(dependency)

            graph.setdefault(dependency, [])

        # Добавляем зависимости в стек
        for dependency in reversed(dependencies):

            if dependency not in visited:
                stack.append(
                    (dependency, None, depth + 1)
                )

    return graph