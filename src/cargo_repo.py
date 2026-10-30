"""Получение прямых зависимостей пакета Rust (Cargo) из репозитория.

Используется открытый API репозитория crates.io и только стандартная
библиотека Python: менеджер пакетов cargo не вызывается.

    {repository}/api/v1/crates/{package}
        сведения о пакете, из них берётся последняя версия;
    {repository}/api/v1/crates/{package}/{version}/dependencies
        зависимости этой версии пакета.
"""
import json
import urllib.error
import urllib.request

from errors import RepositoryError

API_PATH = "/api/v1/crates/"
USER_AGENT = "dependency-graph/1.0 (MIREA student project)"
TIMEOUT = 20
HTTP_NOT_FOUND = 404
DEV_KIND = "dev"


def _get_json(url):
    """Скачать страницу по URL и разобрать её как JSON."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == HTTP_NOT_FOUND:
            raise RepositoryError(
                f"пакет не найден в репозитории: {url}") from err
        raise RepositoryError(
            f"репозиторий вернул ошибку {err.code}: {url}") from err
    except urllib.error.URLError as err:
        raise RepositoryError(
            f"не удалось подключиться к репозиторию: {err.reason}") from err
    except ValueError as err:
        raise RepositoryError(
            f"репозиторий вернул не JSON: {url}") from err
    except OSError as err:
        raise RepositoryError(
            f"ошибка при обращении к репозиторию: {err}") from err


def crate_url(repository, package):
    """Адрес пакета в API репозитория."""
    return repository.rstrip("/") + API_PATH + package


def get_latest_version(repository, package):
    """Узнать последнюю стабильную версию пакета."""
    data = _get_json(crate_url(repository, package))
    try:
        crate = data["crate"]
        version = crate["max_stable_version"] or crate["max_version"]
    except (KeyError, TypeError) as err:
        raise RepositoryError("некорректный ответ репозитория") from err
    if not version:
        raise RepositoryError(f"у пакета {package} нет версий")
    return version


def parse_dependencies(data):
    """Выбрать из ответа API зависимости пакета.

    Зависимости для разработки (kind = dev) нужны только для тестов
    самого пакета и пропускаются. Каждое имя берётся один раз.
    Возвращается словарь «имя -> (требование к версии, необязательная)».
    """
    result = {}
    try:
        for item in data["dependencies"]:
            name = item["crate_id"]
            if item["kind"] != DEV_KIND and name not in result:
                result[name] = (item["req"], item["optional"])
    except (KeyError, TypeError) as err:
        raise RepositoryError("некорректный ответ репозитория") from err
    return result


def get_direct_dependencies(repository, package):
    """Вернуть версию пакета и его прямые зависимости."""
    version = get_latest_version(repository, package)
    url = f"{crate_url(repository, package)}/{version}/dependencies"
    return version, parse_dependencies(_get_json(url))
