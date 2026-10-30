"""Параметры, которые настраивает пользователь, и их проверка."""
import os
import re
from urllib.parse import urlparse

from errors import ConfigError
from yaml_reader import read_yaml

PACKAGE = "package"
REPOSITORY = "repository"
TEST_MODE = "test_mode"
PARAMETERS = (PACKAGE, REPOSITORY, TEST_MODE)
PACKAGE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
URL_SCHEMES = ("http", "https")


def _check_package(value):
    """Имя пакета: латинские буквы, цифры, _ и -, до 64 символов."""
    if not isinstance(value, str) or not value:
        return f"{PACKAGE}: не задано имя анализируемого пакета"
    if not PACKAGE_PATTERN.fullmatch(value):
        return (f"{PACKAGE}: некорректное имя пакета «{value}» "
                "(латинские буквы, цифры, _ и -, начинается с буквы, "
                "не длиннее 64 символов)")
    return None


def _check_test_mode(value):
    """Режим работы с тестовым репозиторием: true или false."""
    if not isinstance(value, bool):
        return f"{TEST_MODE}: ожидается true или false, получено «{value}»"
    return None


def _check_url(value):
    """URL-адрес репозитория: http или https и имя сервера."""
    address = urlparse(value)
    if address.scheme not in URL_SCHEMES or not address.netloc:
        return (f"{REPOSITORY}: некорректный URL-адрес «{value}» "
                "(ожидается http:// или https://)")
    return None


def _check_repository(value, test_mode):
    """URL репозитория или путь к файлу тестового репозитория."""
    if not isinstance(value, str) or not value:
        return f"{REPOSITORY}: не задан репозиторий"
    if test_mode is not True:
        return _check_url(value)
    if not os.path.isfile(value):
        return f"{REPOSITORY}: файл тестового репозитория не найден: {value}"
    return None


def _check_keys(values):
    """Найти пропущенные и лишние параметры."""
    errors = [f"{name}: параметр не задан"
              for name in PARAMETERS if name not in values]
    errors += [f"{name}: неизвестный параметр"
               for name in values if name not in PARAMETERS]
    return errors


def validate(values):
    """Проверить все параметры и вернуть список текстов ошибок."""
    errors = _check_keys(values)
    checks = (
        (PACKAGE, _check_package(values.get(PACKAGE))),
        (TEST_MODE, _check_test_mode(values.get(TEST_MODE))),
        (REPOSITORY, _check_repository(values.get(REPOSITORY),
                                       values.get(TEST_MODE))),
    )
    errors += [message for name, message in checks
               if message and name in values]
    return errors


def load_config(path):
    """Прочитать конфигурацию из YAML-файла и проверить её.

    Если найдены ошибки, бросается ConfigError со всеми ошибками сразу.
    """
    values = read_yaml(path)
    errors = validate(values)
    if errors:
        raise ConfigError("\n".join(errors))
    return {name: values[name] for name in PARAMETERS}
