"""Точка входа: python3 src/main.py [путь к конфигурационному файлу]."""
import sys

from config import load_config
from errors import ConfigError

DEFAULT_CONFIG = "config.yaml"
MAX_ARGS = 1
EXIT_ERROR = 1


def format_value(value):
    """Показать значение так, как оно записывается в YAML."""
    if isinstance(value, bool):
        return str(value).lower()
    return value


def print_parameters(config):
    """Вывести все параметры в формате «ключ = значение»."""
    for key, value in config.items():
        print(f"{key} = {format_value(value)}")


def main(argv=None):
    """Загрузить конфигурацию, вывести её и вернуть код завершения."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) > MAX_ARGS:
        print("использование: main.py [КОНФИГ.yaml]", file=sys.stderr)
        return EXIT_ERROR
    path = args[0] if args else DEFAULT_CONFIG
    try:
        config = load_config(path)
    except ConfigError as err:
        print(f"ошибка конфигурации ({path}):", file=sys.stderr)
        for line in str(err).splitlines():
            print(f"  {line}", file=sys.stderr)
        return EXIT_ERROR
    print_parameters(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
