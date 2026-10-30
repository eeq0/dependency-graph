"""Точка входа: python3 src/main.py [путь к конфигурационному файлу]."""
import sys

from cargo_repo import get_direct_dependencies
from config import PACKAGE, REPOSITORY, TEST_MODE, load_config
from errors import ConfigError, RepositoryError

DEFAULT_CONFIG = "config.yaml"
MAX_ARGS = 1
EXIT_ERROR = 1


def print_error(title, err):
    """Вывести ошибку в stderr: заголовок и строки сообщения с отступом."""
    print(f"{title}:", file=sys.stderr)
    for line in str(err).splitlines():
        print(f"  {line}", file=sys.stderr)


def print_dependencies(package, version, dependencies):
    """Вывести все прямые зависимости пакета."""
    print(f"Прямые зависимости пакета {package} {version}:")
    if not dependencies:
        print("  нет зависимостей")
    for name, (requirement, optional) in sorted(dependencies.items()):
        mark = " (необязательная)" if optional else ""
        print(f"  {name} {requirement}{mark}")


def run(config):
    """Получить и вывести прямые зависимости пакета из конфигурации."""
    if config[TEST_MODE]:
        print("режим тестового репозитория появится на этапе 3",
              file=sys.stderr)
        return EXIT_ERROR
    package = config[PACKAGE]
    try:
        version, dependencies = get_direct_dependencies(
            config[REPOSITORY], package)
    except RepositoryError as err:
        print_error(f"ошибка репозитория (пакет {package})", err)
        return EXIT_ERROR
    print_dependencies(package, version, dependencies)
    return 0


def main(argv=None):
    """Загрузить конфигурацию, выполнить работу и вернуть код завершения."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) > MAX_ARGS:
        print("использование: main.py [КОНФИГ.yaml]", file=sys.stderr)
        return EXIT_ERROR
    path = args[0] if args else DEFAULT_CONFIG
    try:
        config = load_config(path)
    except ConfigError as err:
        print_error(f"ошибка конфигурации ({path})", err)
        return EXIT_ERROR
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
