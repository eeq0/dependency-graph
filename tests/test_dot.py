"""Тесты представления графа на языке Graphviz (DOT)."""
import unittest

import helpers
from dot import quote, to_dot

HEADER = ["digraph dependencies {", "    node [shape=box];"]


def dot_lines(root, graph, reverse=False):
    """Строки DOT-описания графа."""
    return to_dot(root, graph, reverse).splitlines()


class DotTest(unittest.TestCase):
    """Формирование описания графа."""

    def test_single_package(self):
        """Пакет без зависимостей: только выделенная вершина."""
        self.assertEqual(dot_lines("A", {"A": []}), HEADER + [
            '    "A" [style=filled, fillcolor=lightblue];', "}"])

    def test_edges_in_bfs_order(self):
        """Рёбра «пакет -> зависимость» в порядке обхода, цикл тоже."""
        graph = {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
        self.assertEqual(dot_lines("A", graph)[len(HEADER) + 1:], [
            '    "A" -> "B";', '    "A" -> "C";', '    "B" -> "C";',
            '    "C" -> "A";', "}"])

    def test_reverse_edges(self):
        """В обратном режиме стрелка всё равно означает «зависит от»."""
        graph = {"D": ["B", "C"], "B": ["A"], "C": ["A"], "A": []}
        edges = dot_lines("D", graph, reverse=True)[len(HEADER) + 1:-1]
        self.assertEqual(edges, ['    "B" -> "D";', '    "C" -> "D";',
                                 '    "A" -> "B";', '    "A" -> "C";'])

    def test_quote(self):
        """Имена с дефисом и кавычкой записываются в кавычках."""
        self.assertEqual(quote("proc-macro2"), '"proc-macro2"')
        self.assertEqual(quote('a"b'), '"a\\"b"')

    def test_temp_file_helper(self):
        """DOT можно сохранить в файл и прочитать обратно без изменений."""
        text = to_dot("A", {"A": ["B"], "B": []})
        path = helpers.write_temp(self, text, ".dot")
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), text)


if __name__ == "__main__":
    unittest.main()
