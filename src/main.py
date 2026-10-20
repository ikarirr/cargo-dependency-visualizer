import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from .dependencies import get_dependencies
except ImportError:
    from dependencies import get_dependencies

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
        raise ValueError("Корневой элемент должен называться config")

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
            raise ValueError(f"Отсутствует параметр: {param}")

        config[param] = element.text.strip()

    if not config["package_name"]:
        raise ValueError("Название пакета не может быть пустым")

    if not config["repository_url"].startswith(("http://", "https://")):
        raise ValueError("Некорректный URL репозитория")

    if config["test_mode"].lower() not in ("true", "false"):
        raise ValueError("Режим тестирования должен быть true или false")

    config["test_mode"] = config["test_mode"].lower() == "true"

    if not config["package_version"]:
        raise ValueError("Версия пакета не может быть пустой")

    if config["output_mode"] not in ("ascii", "graph"):
        raise ValueError("Режим вывода должен быть ascii или graph")

    try:
        config["max_depth"] = int(config["max_depth"])

        if config["max_depth"] < 0:
            raise ValueError("Глубина анализа не может быть отрицательной")

    except ValueError:
        raise ValueError("Глубина анализа должна быть целым неотрицательным числом")

    return config

def main():
    """Главная функция программы."""

    config_path = Path(__file__).resolve().parent.parent / "config.xml"

    try:
        config = load_config(config_path)

        print("=== Визуализатор зависимостей Cargo ===")
        print("Конфигурация успешно загружена!\n")

        print(f"Название пакета: {config['package_name']}")
        print(f"URL репозитория: {config['repository_url']}")
        print(f"Режим тестирования: {config['test_mode']}")
        print(f"Версия пакета: {config['package_version']}")
        print(f"Режим вывода: {config['output_mode']}")
        print(f"Максимальная глубина: {config['max_depth']}")
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

    except ValueError as error:
        print(f"Ошибка конфигурации: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()