"""Обращение к HTTP API crates.io за версиями и зависимостями пакетов."""

import json
import urllib.error
import urllib.parse
import urllib.request


def api_request(url):
    """Отправить GET-запрос и разобрать JSON с понятными ошибками сети."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CargoDependencyVisualizer/1.0",
            "Accept": "application/json",
        },
    )
    try:
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
        raise ValueError("Репозиторий вернул некорректные данные") from error


def _crate_api_url(repository_url, package_name, version=None):
    """Собрать URL API, безопасно кодируя имя пакета и его версию."""
    base_url = repository_url.rstrip("/")
    encoded_name = urllib.parse.quote(package_name, safe="")
    url = f"{base_url}/api/v1/crates/{encoded_name}"
    if version is not None:
        encoded_version = urllib.parse.quote(version, safe="")
        url = f"{url}/{encoded_version}/dependencies"
    return url


def get_latest_version(package_name, repository_url):
    """Получить последнюю стабильную версию или последнюю доступную."""
    if not package_name:
        raise ValueError("Необходимо указать имя пакета")
    data = api_request(_crate_api_url(repository_url, package_name))
    crate = data.get("crate", {})
    version = crate.get("max_stable_version") or crate.get("max_version")
    if not version:
        raise ValueError(
            f"Не удалось определить версию пакета {package_name}"
        )
    return version


def _extract_dependency_names(data):
    """Проверить ответ API и вернуть имена уникальных зависимостей."""
    if not isinstance(data, dict) or not isinstance(
        data.get("dependencies"), list
    ):
        raise ValueError("Неверный формат данных репозитория")

    dependencies = set()
    for dependency in data["dependencies"]:
        if not isinstance(dependency, dict):
            raise ValueError("Неверный формат данных репозитория")
        name = dependency.get("crate_id")
        if name:
            dependencies.add(name)
    return sorted(dependencies)


def get_dependencies(package_name, version, repository_url):
    """Получить прямые зависимости выбранной версии пакета Cargo."""
    if not package_name:
        raise ValueError("Необходимо указать имя пакета")
    if not repository_url:
        raise ValueError("Необходимо указать адрес репозитория")
    if version is None:
        version = get_latest_version(package_name, repository_url)
    if not version:
        raise ValueError("Необходимо указать версию пакета")

    url = _crate_api_url(repository_url, package_name, version)
    return _extract_dependency_names(api_request(url))