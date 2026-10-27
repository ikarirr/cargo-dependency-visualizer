"""Точка входа визуализатора зависимостей пакетов Cargo."""

import shutil
import subprocess
import sys
import xml.etree.ElementTree as element_tree
from pathlib import Path

try:
    from .dependencies import get_dependencies
    from .graph import build_graph
    from .visualization import generate_ascii_tree, save_d2
except ImportError:
    from dependencies import get_dependencies
    from graph import build_graph
    from visualization import generate_ascii_tree, save_d2

REQUIRED_PARAMS = (
    "package_name",
    "repository_url",
    "test_mode",
    "package_version",
    "output_mode",
    "max_depth",
)


def _read_xml_root(config_path):
    """Прочитать XML и вернуть корневой элемент."""
    try:
        tree = element_tree.parse(config_path)
    except FileNotFoundError as error:
        raise ValueError(
            "Файл конфигурации не найден"
        ) from error
    except element_tree.ParseError as error:
        raise ValueError(
            "Ошибка в структуре XML-файла"
        ) from error

    return tree.getroot()


def _read_required_parameters(root):
    """Получить обязательные параметры конфигурации."""
    if root.tag != "config":
        raise ValueError(
            "Корневой элемент должен называться config"
        )

    config = {}

    for param in REQUIRED_PARAMS:
        element = root.find(param)

        if element is None:
            raise ValueError(
                f"Отсутствует параметр: {param}"
            )

        if element.text is None or not element.text.strip():
            raise ValueError(
                f"Отсутствует параметр: {param}"
            )

        config[param] = element.text.strip()

    return config


def _parse_test_mode(value):
    """Преобразовать текстовое значение в bool."""
    normalized = value.lower()

    if normalized not in ("true", "false"):
        raise ValueError(
            "Режим тестирования должен быть true или false"
        )

    return normalized == "true"


def _parse_max_depth(value):
    """Проверить максимальную глубину обхода."""
    try:
        depth = int(value)
    except ValueError as error:
        raise ValueError(
            "Глубина анализа должна быть целым числом"
        ) from error

    if depth < 0:
        raise ValueError(
            "Глубина анализа не может быть отрицательной"
        )

    return depth


def load_config(config_path):
    """Загрузить и проверить XML-конфигурацию."""
    root = _read_xml_root(config_path)
    config = _read_required_parameters(root)

    repository_url = config["repository_url"]

    if not repository_url.startswith(
        ("http://", "https://")
    ):
        raise ValueError(
            "Некорректный URL репозитория"
        )

    if config["output_mode"] not in ("ascii", "graph"):
        raise ValueError(
            "Режим вывода должен быть ascii или graph"
        )

    config["test_mode"] = _parse_test_mode(
        config["test_mode"]
    )

    config["max_depth"] = _parse_max_depth(
        config["max_depth"]
    )

    return config


def _print_config(config):
    """Вывести параметры конфигурации."""
    print("=== Визуализатор зависимостей Cargo ===")
    print("Конфигурация успешно загружена!\n")

    print(f"Название пакета: {config['package_name']}")
    print(f"URL репозитория: {config['repository_url']}")
    print(f"Режим тестирования: {config['test_mode']}")
    print(f"Версия пакета: {config['package_version']}")
    print(f"Режим вывода: {config['output_mode']}")
    print(f"Максимальная глубина: {config['max_depth']}")


def _print_direct_dependencies(config):
    """Получить и вывести прямые зависимости."""
    print("\n=== Прямые зависимости пакета ===")

    dependencies = get_dependencies(
        config["package_name"],
        config["package_version"],
        config["repository_url"],
    )

    if not dependencies:
        print("Прямые зависимости отсутствуют")
        return

    for dependency in dependencies:
        print(f"- {dependency}")


def _build_and_print_graph(config):
    """Построить граф и вывести его связи."""

    print("\n=== Построение графа зависимостей ===")

    graph = build_graph(
        config["package_name"],
        config["package_version"],
        config["repository_url"],
        config["max_depth"],
    )

    print("Граф зависимостей успешно построен!")

    for package, dependencies in graph.items():
        print(f"{package}: {dependencies}")

    return graph


def _find_d2_executable():
    """Найти исполняемый файл D2."""
    executable = shutil.which("d2")

    if executable:
        return executable

    installed = Path(r"C:\Program Files\D2\d2.exe")

    if installed.is_file():
        return str(installed)

    return None


def _run_d2(executable, d2_path, svg_path):
    """Запустить D2 для создания SVG-файла."""
    return subprocess.run(
        [executable, str(d2_path), str(svg_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _export_svg(graph, project_dir):
    """Создать D2-файл и преобразовать его в SVG."""
    print("\n=== Визуализация графа D2 ===")

    d2_path = project_dir / "graph.d2"
    svg_path = project_dir / "graph.svg"

    save_d2(graph, str(d2_path))
    print(f"Файл D2 создан: {d2_path}")

    executable = _find_d2_executable()

    if executable is None:
        print("D2 не найден.")
        print("Файл graph.d2 успешно сохранён.")
        print("SVG можно создать вручную через D2.")
        return

    result = _run_d2(
        executable,
        d2_path,
        svg_path,
    )

    if result.returncode != 0:
        print("Ошибка при создании SVG:")
        print(result.stderr)
        return

    print("Граф успешно визуализирован!")
    print(f"SVG-файл: {svg_path}")


def _show_visualization(graph, config, project_dir):
    """Выбрать способ отображения графа."""
    if config["output_mode"] == "ascii":
        print("\n=== ASCII-дерево зависимостей ===")

        tree = generate_ascii_tree(
            graph,
            config["package_name"],
        )

        print(tree)
        return

    _export_svg(graph, project_dir)


def main():
    """Запустить визуализатор зависимостей."""
    project_dir = Path(__file__).resolve().parent.parent

    try:
        config_path = project_dir / "config.xml"
        config = load_config(config_path)

        _print_config(config)
        _print_direct_dependencies(config)

        graph = _build_and_print_graph(config)

        _show_visualization(
            graph,
            config,
            project_dir,
        )

        print("\n=== Работа программы завершена ===")

    except (ValueError, OSError) as error:
        print(f"\nОшибка: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
