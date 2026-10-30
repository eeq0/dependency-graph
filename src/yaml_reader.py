"""Чтение конфигурационного файла в формате YAML.

Поддерживается подмножество YAML, которого достаточно для конфигурации:
пары «ключ: значение» на верхнем уровне, комментарии после #,
строки в кавычках и логические значения true/false.
"""
from errors import ConfigError

COMMENT = "#"
SEPARATOR = ":"
QUOTES = ("'", '"')
BOOLEANS = {"true": True, "false": False}
NOT_FOUND = -1


def _strip_comment(value):
    """Убрать комментарий в конце значения без кавычек."""
    position = value.find(" " + COMMENT)
    if position == NOT_FOUND:
        return value
    return value[:position].rstrip()


def _parse_value(raw, number):
    """Превратить текст значения в строку или логическое значение."""
    value = raw.strip()
    if value[:1] in QUOTES:
        end = value.find(value[0], 1)
        if end == NOT_FOUND:
            raise ConfigError(f"строка {number}: незакрытая кавычка")
        return value[1:end]
    value = _strip_comment(value)
    return BOOLEANS.get(value.lower(), value)


def _parse_line(line, number):
    """Разобрать одну строку «ключ: значение» и вернуть пару."""
    if line[0].isspace():
        raise ConfigError(
            f"строка {number}: вложенные значения не поддерживаются")
    key, separator, raw = line.partition(SEPARATOR)
    key = key.strip()
    if not separator or not key:
        raise ConfigError(
            f"строка {number}: ожидается запись вида «ключ: значение»")
    return key, _parse_value(raw, number)


def parse_yaml(text):
    """Разобрать текст YAML и вернуть словарь «ключ -> значение»."""
    result = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith(COMMENT):
            continue
        key, value = _parse_line(line, number)
        if key in result:
            raise ConfigError(f"строка {number}: ключ «{key}» повторяется")
        result[key] = value
    return result


def read_yaml(path):
    """Прочитать YAML-файл с диска и вернуть словарь значений."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError as err:
        raise ConfigError(
            f"конфигурационный файл не найден: {path}") from err
    except (OSError, UnicodeError) as err:
        raise ConfigError(
            f"не удалось прочитать конфигурационный файл: {path}") from err
    return parse_yaml(text)
