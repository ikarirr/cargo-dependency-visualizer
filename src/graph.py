"""Построение графа зависимостей Cargo обходом DFS без рекурсии."""

from collections import deque

try:
    from .dependencies import get_dependencies, get_latest_version
except ImportError:
    from dependencies import get_dependencies, get_latest_version


def _validate_graph_parameters(package_name, max_depth):
    """Проверить название корневого пакета и глубину обхода."""
    if not package_name:
        raise ValueError("Название пакета не может быть пустым")
    if not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError("Глубина должна быть неотрицательным числом")


def _fetch_dependencies(package, version, repository_url, provider):
    """Получить зависимости, определив версию при необходимости."""
    if version is None:
        version = get_latest_version(package, repository_url)
    return provider(package, version, repository_url)


def _add_graph_edges(graph, package, dependencies):
    """Зарегистрировать узлы и связи без дублирования рёбер."""
    for dependency in dependencies:
        if dependency not in graph[package]:
            graph[package].append(dependency)
        graph.setdefault(dependency, [])


def _push_unvisited(stack, dependencies, visited, depth):
    """Добавить соседей в стек в порядке, сохраняющем порядок DFS."""
    for dependency in reversed(dependencies):
        if dependency not in visited:
            stack.append((dependency, None, depth + 1))


def build_graph(
    package_name,
    package_version,
    repository_url,
    max_depth,
    dependency_provider=None,
):
    """Построить граф до max_depth с помощью итеративного обхода DFS."""
    _validate_graph_parameters(package_name, max_depth)
    provider = dependency_provider
    if provider is None:
        provider = get_dependencies
    graph = {}
    visited = set()
    stack = deque([(package_name, package_version, 0)])

    while stack:
        package, version, depth = stack.pop()
        if package in visited:
            continue

        visited.add(package)
        graph.setdefault(package, [])
        if depth >= max_depth:
            continue

        dependencies = _fetch_dependencies(
            package, version, repository_url, provider
        )
        _add_graph_edges(graph, package, dependencies)
        _push_unvisited(stack, dependencies, visited, depth)

    return graph