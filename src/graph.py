from collections import deque

from src.dependencies import get_dependencies, get_latest_version

def build_graph(
    package_name,
    package_version,
    repository_url,
    max_depth,
    get_dependencies_func=None
):
    """
    Построение графа зависимостей пакета Cargo.

    package_name — название исходного пакета.
    package_version — версия исходного пакета.
    repository_url — адрес репозитория.
    max_depth — максимальная глубина анализа.
    get_dependencies_func — функция получения зависимостей.
    """

    if not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError(
            "Максимальная глубина должна быть целым "
            "неотрицательным числом"
        )

    if not package_name or not package_version:
        raise ValueError(
            "Необходимо указать название и версию пакета"
        )

    if get_dependencies_func is None:
        get_dependencies_func = get_dependencies

    graph = {}
    visited = set()

    queue = deque([
        (package_name, package_version, 0)
    ])

    while queue:
        current_package, current_version, depth = queue.popleft()

        if current_package in visited:
            continue

        visited.add(current_package)

        graph.setdefault(current_package, [])

        if depth >= max_depth:
            continue

        try:
            if current_version is None:
                current_version = get_latest_version(
                    current_package,
                    repository_url
                )

            dependencies = get_dependencies_func(
                current_package,
                current_version,
                repository_url
            )

        except ValueError as error:
            print(
                f"Ошибка получения зависимостей "
                f"пакета {current_package}: {error}"
            )
            continue

        for dependency in dependencies:

            if dependency not in graph[current_package]:
                graph[current_package].append(dependency)

            graph.setdefault(dependency, [])

            if dependency not in visited:
                queue.append(
                    (dependency, None, depth + 1)
                )

    return graph