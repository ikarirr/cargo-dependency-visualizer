import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from .dependencies import get_dependencies
    from .graph import build_graph
    from .visualization import generate_ascii_tree, save_d2

except ImportError:
    from dependencies import get_dependencies
    from graph import build_graph
    from visualization import generate_ascii_tree, save_d2

def load_config(config_path):
    """Загрузка и проверка XML-конфигурации."""

    try:
        tree = ET.parse(config_path)
        root = tree.getroot()

    except FileNotFoundError:
        raise ValueError("Файл конфигурации не найден")

    except ET.ParseError:
        raise ValueError("Ошибка в структуре XML-файла")

    if root.tag != "config":
        raise ValueError(
            "Корневой элемент должен называться config"
        )

    required_params = [
        "package_name",
        "repository_url",
        "test_mode",
        "package_version",
        "output_mode",
        "max_depth"
    ]

    config = {}

    for param in required_params:
        element = root.find(param)

        if element is None or not element.text or not element.text.strip():
            raise ValueError(
                f"Отсутствует параметр: {param}"
            )

        config[param] = element.text.strip()

    if not config["repository_url"].startswith(
        ("http://", "https://")
    ):
        raise ValueError("Некорректный URL репозитория")

    if config["test_mode"].lower() not in ("true", "false"):
        raise ValueError(
            "Режим тестирования должен быть true или false"
        )

    config["test_mode"] = (
        config["test_mode"].lower() == "true"
    )

    if config["output_mode"] not in ("ascii", "graph"):
        raise ValueError(
            "Режим вывода должен быть ascii или graph"
        )

    try:
        max_depth = int(config["max_depth"])

    except ValueError:
        raise ValueError(
            "Глубина анализа должна быть целым числом"
        )

    if max_depth < 0:
        raise ValueError(
            "Глубина анализа не может быть отрицательной"
        )

    config["max_depth"] = max_depth

    return config

def main():
    """Главная функция визуализатора зависимостей."""

    project_dir = Path(__file__).resolve().parent.parent
    config_path = project_dir / "config.xml"

    try:
        # Этап 1. Загрузка XML-конфигурации

        config = load_config(config_path)

        print("=== Визуализатор зависимостей Cargo ===")
        print("Конфигурация успешно загружена!\n")

        print(f"Название пакета: {config['package_name']}")
        print(f"URL репозитория: {config['repository_url']}")
        print(f"Режим тестирования: {config['test_mode']}")
        print(f"Версия пакета: {config['package_version']}")
        print(f"Режим вывода: {config['output_mode']}")
        print(f"Максимальная глубина: {config['max_depth']}")

        # Этап 2. Получение прямых зависимостей

        print("\n=== Прямые зависимости пакета ===")

        dependencies = get_dependencies(
            config["package_name"],
            config["package_version"],
            config["repository_url"]
        )

        if dependencies:
            for dependency in dependencies:
                print(f"- {dependency}")
        else:
            print("Прямые зависимости отсутствуют")

        # Этап 3. Построение графа зависимостей

        print("\n=== Построение графа зависимостей ===")

        graph = build_graph(
            config["package_name"],
            config["package_version"],
            config["repository_url"],
            config["max_depth"]
        )

        print("Граф зависимостей успешно построен!")

        for package, package_dependencies in graph.items():
            print(f"{package}: {package_dependencies}")

        # Этап 5. Визуализация графа

        if config["output_mode"] == "ascii":

            print("\n=== ASCII-дерево зависимостей ===")

            ascii_tree = generate_ascii_tree(
                graph,
                config["package_name"]

            )

            print(ascii_tree)

        elif config["output_mode"] == "graph":

            print("\n=== Визуализация графа D2 ===")

            d2_path = project_dir / "graph.d2"
            svg_path = project_dir / "graph.svg"

            save_d2(graph, str(d2_path))

            print(f"Файл D2 создан: {d2_path}")

            # Путь к установленному D2

            d2_executable = Path(
                r"C:\Program Files\D2\d2.exe"
            )

            if d2_executable.exists():

                result = subprocess.run(
                    [
                        str(d2_executable),
                        str(d2_path),
                        str(svg_path)
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

                if result.returncode == 0:

                    print("Граф успешно визуализирован!")
                    print(f"SVG-файл: {svg_path}")

                else:

                    print("Ошибка при создании SVG:")
                    print(result.stderr)

            else:

                print("D2 не найден по указанному пути.")
                print("Файл graph.d2 успешно сохранён.")
                print("SVG можно создать вручную через D2.")

        print("\n=== Работа программы завершена ===")

    except (ValueError, OSError) as error:

        print(f"\nОшибка: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()