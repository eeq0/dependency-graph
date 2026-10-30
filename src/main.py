"""Точка входа: python3 src/main.py [путь к конфигурационному файлу]."""
import sys
from functools import partial

from cargo_repo import get_dependency_names
from config import PACKAGE, REPOSITORY, REVERSE, TEST_MODE, load_config
from dot import to_dot
from errors import ConfigError, RepositoryError
from graph import build_graph, reverse_edges
from test_repo import get_test_dependencies, read_test_repo

DEFAULT_CONFIG = "config.yaml"
MAX_ARGS = 1
EXIT_ERROR = 1


def print_error(title, err):
    """Вывести ошибку в stderr: заголовок и строки сообщения с отступом."""
    print(f"{title}:", file=sys.stderr)
    for line in str(err).splitlines():
        print(f"  {line}", file=sys.stderr)


def make_source(config):
    """Выбрать, откуда брать рёбра графа: тестовый файл или crates.io."""
    if config[TEST_MODE]:
        packages = read_test_repo(config[REPOSITORY])
        if config[REVERSE]:
            packages = reverse_edges(packages)
        return partial(get_test_dependencies, packages)
    return partial(get_dependency_names, config[REPOSITORY])


def run(config):
    """Построить граф пакета и вывести его на языке Graphviz (DOT)."""
    package = config[PACKAGE]
    try:
        graph = build_graph(package, make_source(config))
    except RepositoryError as err:
        print_error(f"ошибка репозитория (пакет {package})", err)
        return EXIT_ERROR
    print(to_dot(package, graph, config[REVERSE]))
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
