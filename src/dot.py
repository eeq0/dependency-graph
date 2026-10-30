"""Текстовое представление графа на языке диаграмм Graphviz (DOT).

Пример результата для пакета A, который зависит от B:

    digraph dependencies {
        node [shape=box];
        "A" [style=filled, fillcolor=lightblue];
        "A" -> "B";
    }
"""
INDENT = "    "


def quote(name):
    """Записать имя пакета в кавычках, как требует DOT."""
    return '"' + name.replace('"', '\\"') + '"'


def to_dot(root, graph, reverse=False):
    """Описать граф на языке DOT.

    graph: словарь «пакет -> список пакетов», построенный обходом BFS.
    Стрелка A -> B всегда означает «A зависит от B». В режиме обратных
    зависимостей граф хранит «пакет -> кто от него зависит», поэтому
    рёбра разворачиваются. Анализируемый пакет выделяется цветом.
    """
    lines = ["digraph dependencies {",
             f"{INDENT}node [shape=box];",
             f"{INDENT}{quote(root)} [style=filled, fillcolor=lightblue];"]
    for name, targets in graph.items():
        for target in targets:
            start, end = (target, name) if reverse else (name, target)
            lines.append(f"{INDENT}{quote(start)} -> {quote(end)};")
    lines.append("}")
    return "\n".join(lines)
