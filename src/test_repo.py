"""Тестовый репозиторий: граф пакетов, описанный в текстовом файле.

Пакеты называются большими латинскими буквами. Каждая строка файла
описывает один пакет и его прямые зависимости через пробел:

    A: B C
    B: D
    C: D
    D:

Пустые строки и комментарии после # пропускаются.
"""
import re

from errors import RepositoryError

NAME_PATTERN = re.compile(r"[A-Z]+")
SEPARATOR = ":"
COMMENT = "#"


def _check_name(name, number):
    """Имя пакета: только большие латинские буквы."""
    if not NAME_PATTERN.fullmatch(name):
        raise RepositoryError(
            f"строка {number}: некорректное имя пакета «{name}» "
            "(только большие латинские буквы)")


def _parse_line(line, number):
    """Разобрать строку «A: B C» и вернуть имя и список зависимостей."""
    name, separator, rest = line.partition(SEPARATOR)
    if not separator:
        raise RepositoryError(
            f"строка {number}: ожидается запись вида «A: B C»")
    name = name.strip()
    dependencies = list(dict.fromkeys(rest.split()))
    for item in [name] + dependencies:
        _check_name(item, number)
    return name, dependencies


def parse_test_repo(text):
    """Разобрать текст тестового репозитория в словарь «пакет -> список»."""
    packages = {}
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.split(COMMENT)[0].strip()
        if not line:
            continue
        name, dependencies = _parse_line(line, number)
        if name in packages:
            raise RepositoryError(
                f"строка {number}: пакет {name} описан повторно")
        packages[name] = dependencies
    return packages


def read_test_repo(path):
    """Прочитать файл тестового репозитория."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeError) as err:
        raise RepositoryError(
            f"не удалось прочитать тестовый репозиторий: {path}") from err
    return parse_test_repo(text)


def get_test_dependencies(packages, name):
    """Прямые зависимости пакета из тестового репозитория."""
    if name not in packages:
        raise RepositoryError(
            f"пакет {name} не описан в тестовом репозитории")
    return packages[name]
