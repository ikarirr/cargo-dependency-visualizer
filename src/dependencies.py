import json
import urllib.error
import urllib.parse
import urllib.request

def api_request(url):
    """Выполнение запроса к API Cargo."""

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "CargoDependencyVisualizer/1.0",
                "Accept": "application/json"
            }
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    except urllib.error.HTTPError as error:
        raise ValueError(
            f"Ошибка HTTP {error.code}: не удалось получить данные"
        ) from error

    except urllib.error.URLError as error:
        raise ValueError(
            f"Ошибка подключения к репозиторию: {error.reason}"
        ) from error

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(
            "Репозиторий вернул некорректные данные"
        ) from error

def get_latest_version(package_name, repository_url):
    """Получение последней стабильной версии пакета."""

    if not package_name:
        raise ValueError("Необходимо указать имя пакета")

    base_url = repository_url.rstrip("/")

    encoded_name = urllib.parse.quote(package_name, safe="")

    url = f"{base_url}/api/v1/crates/{encoded_name}"

    data = api_request(url)

    crate = data.get("crate", {})

    version = crate.get("max_stable_version")

    if not version:
        version = crate.get("max_version")

    if not version:
        raise ValueError(
            f"Не удалось определить версию пакета {package_name}"
        )

    return version

def get_dependencies(package_name, version, repository_url):
    """Получение прямых зависимостей пакета Cargo."""

    if not package_name:
        raise ValueError("Необходимо указать имя пакета")

    if not repository_url:
        raise ValueError("Необходимо указать адрес репозитория")

    base_url = repository_url.rstrip("/")

    # Если версия не указана, определяем её автоматически
    if version is None:
        version = get_latest_version(
            package_name,
            repository_url
        )

    if not version:
        raise ValueError("Необходимо указать версию пакета")

    encoded_name = urllib.parse.quote(package_name, safe="")
    encoded_version = urllib.parse.quote(version, safe="")

    url = (
        f"{base_url}/api/v1/crates/"
        f"{encoded_name}/{encoded_version}/dependencies"
    )

    data = api_request(url)

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