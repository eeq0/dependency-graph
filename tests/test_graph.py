"""Тесты построения графа обходом BFS с рекурсией."""
import unittest
from functools import partial

import helpers
from errors import RepositoryError
from graph import build_graph, reverse_edges
from test_repo import get_test_dependencies, read_test_repo


def graph_of(test, text, root="A", reverse=False):
    """Записать тестовый репозиторий в файл и построить по нему граф."""
    packages = read_test_repo(helpers.write_temp(test, text, ".txt"))
    if reverse:
        packages = reverse_edges(packages)
    return build_graph(root, partial(get_test_dependencies, packages))


class GraphTest(unittest.TestCase):
    """Разные случаи тестового репозитория."""

    def test_single_package(self):
        """Пакет без зависимостей."""
        self.assertEqual(graph_of(self, "A:"), {"A": []})

    def test_diamond(self):
        """Общая зависимость D попадает в граф один раз."""
        graph = graph_of(self, "A: B C\nB: D\nC: D\nD:")
        self.assertEqual(graph, {"A": ["B", "C"], "B": ["D"], "C": ["D"],
                                 "D": []})

    def test_bfs_order(self):
        """Пакеты идут по уровням: сначала ближние, потом дальние."""
        graph = graph_of(self, "A: B C\nB: D\nC: E\nD: F\nE:\nF:")
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E", "F"])

    def test_cycle(self):
        """Цикл A -> B -> C -> A не зацикливает обход."""
        graph = graph_of(self, "A: B\nB: C\nC: A")
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": ["A"]})

    def test_self_loop(self):
        """Пакет, зависящий сам от себя."""
        graph = graph_of(self, "A: A B\nB:")
        self.assertEqual(graph, {"A": ["A", "B"], "B": []})

    def test_only_reachable(self):
        """В граф попадают только пакеты, достижимые из корня."""
        text = "A: B C D\nB: E\nC: G\nD: A\nE:\nG: C\nX: A"
        graph = graph_of(self, text, root="C")
        self.assertEqual(graph, {"C": ["G"], "G": ["C"]})

    def test_undefined_package(self):
        """Ссылка на неописанный пакет даёт RepositoryError."""
        with self.assertRaisesRegex(RepositoryError, "D не описан"):
            graph_of(self, "A: B\nB: D")

    def test_unknown_root(self):
        """Анализируемого пакета нет в репозитории."""
        with self.assertRaisesRegex(RepositoryError, "Z не описан"):
            graph_of(self, "A:", root="Z")


class ReverseTest(unittest.TestCase):
    """Обратные зависимости тем же обходом BFS."""

    def test_reverse_edges(self):
        """Рёбра переворачиваются, у каждого пакета есть запись."""
        self.assertEqual(reverse_edges({"A": ["B", "C"], "B": ["C"],
                                        "C": []}),
                         {"A": [], "B": ["A"], "C": ["A", "B"]})

    def test_diamond(self):
        """От D зависят B и C напрямую и A через них."""
        graph = graph_of(self, "A: B C\nB: D\nC: D\nD:", root="D",
                         reverse=True)
        self.assertEqual(graph, {"D": ["B", "C"], "B": ["A"], "C": ["A"],
                                 "A": []})

    def test_nobody_depends(self):
        """От корневого пакета никто не зависит."""
        graph = graph_of(self, "A: B\nB:", reverse=True)
        self.assertEqual(graph, {"A": []})

    def test_cycle(self):
        """Цикл в обратную сторону тоже не зацикливает обход."""
        graph = graph_of(self, "A: B\nB: C\nC: A", reverse=True)
        self.assertEqual(graph, {"A": ["C"], "C": ["B"], "B": ["A"]})


if __name__ == "__main__":
    unittest.main()
