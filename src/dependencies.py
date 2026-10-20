import json
import urllib.error
import urllib.parse
import urllib.request

def get_dependencies(package_name, version, repository_url):
    """Получение прямых зависимостей пакета Cargo."""

    if not package_name or not version:
        raise ValueError("Необходимо указать имя и версию пакета")

    # Формируем адрес запроса к реестру Cargo
    base_url = repository_url.rstrip("/")

    url = (
        f"{base_url}/api/v1/crates/"
        f"{urllib.parse.quote(package_name, safe='')}/"
        f"{urllib.parse.quote(version, safe='')}/dependencies"
    )

    try:
        # Отправляем HTTP-запрос
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "CargoDependencyVisualizer/1.0",
                "Accept": "application/json"
            }
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.load(response)

    except urllib.error.HTTPError as error:
        raise ValueError(
            f"Ошибка HTTP {error.code}: не удалось получить зависимости"
        ) from error

    except urllib.error.URLError as error:
        raise ValueError(
            f"Ошибка подключения к репозиторию: {error.reason}"
        ) from error

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(
            "Репозиторий вернул некорректные данные"
        ) from error

    # Проверяем структуру ответа
    if not isinstance(data, dict) or not isinstance(
        data.get("dependencies"), list
    ):
        raise ValueError("Неверный формат данных репозитория")

    dependencies = set()

    for dependency in data["dependencies"]:
        name = dependency.get("crate_id")

        if name:
            dependencies.add(name)

    return sorted(dependencies)