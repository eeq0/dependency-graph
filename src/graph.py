"""Построение графа зависимостей обходом в ширину (BFS) с рекурсией.

Граф хранится как словарь «пакет -> список его прямых зависимостей».
Обход идёт по уровням: сначала сам пакет, затем его прямые зависимости,
затем их зависимости и так далее. Каждый следующий уровень
обрабатывается рекурсивным вызовом той же функции.

Циклы (A -> B -> A) не приводят к бесконечному обходу: пакет, который
уже есть в графе или уже стоит в очереди, второй раз не добавляется.
"""


def _visit_level(level, get_dependencies, graph):
    """Обработать один уровень BFS и рекурсивно перейти к следующему."""
    next_level = []
    for name in level:
        dependencies = get_dependencies(name)
        graph[name] = dependencies
        for dependency in dependencies:
            if (dependency not in graph and dependency not in level
                    and dependency not in next_level):
                next_level.append(dependency)
    if next_level:
        _visit_level(next_level, get_dependencies, graph)


def build_graph(root, get_dependencies):
    """Построить граф всех (в том числе транзитивных) зависимостей.

    get_dependencies(name) возвращает список прямых зависимостей пакета.
    Порядок ключей в результате совпадает с порядком обхода в ширину.
    """
    graph = {}
    _visit_level([root], get_dependencies, graph)
    return graph
