"""Тесты запуска приложения."""
import contextlib
import io
import unittest
from unittest import mock

import helpers
from errors import RepositoryError
from main import main

REAL_CONFIG = ("package: serde\nrepository: https://crates.io\n"
               "test_mode: false\n")
FETCH = "main.get_dependency_names"
FAKE_CRATES = {"serde": ["serde_core"], "serde_core": []}


def run_main(argv):
    """Запустить main и вернуть (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def make_test_config(test, repo_text, package="A", reverse="false"):
    """Создать файл тестового репозитория и конфигурацию для него."""
    repo = helpers.write_temp(test, repo_text, ".txt")
    return helpers.write_temp(
        test, f"package: {package}\nrepository: {repo}\ntest_mode: true\n"
              f"reverse: {reverse}\n")


class MainTest(unittest.TestCase):
    """Вывод графа на языке DOT и ошибок."""

    def test_test_repo_graph(self):
        """Граф тестового репозитория с циклом на языке DOT."""
        code, out, _ = run_main([make_test_config(self, "A: B C\nB: A\nC:")])
        self.assertEqual(code, 0)
        self.assertEqual(out, "digraph dependencies {\n"
                              "    node [shape=box];\n"
                              '    "A" [style=filled, fillcolor=lightblue];\n'
                              '    "A" -> "B";\n'
                              '    "A" -> "C";\n'
                              '    "B" -> "A";\n'
                              "}\n")

    def test_reverse(self):
        """Обратные зависимости D в ромбе: стрелки идут к D."""
        config = make_test_config(self, "A: B C\nB: D\nC: D\nD:", "D",
                                  "true")
        code, out, _ = run_main([config])
        self.assertEqual(code, 0)
        for edge in ('"B" -> "D"', '"C" -> "D"', '"A" -> "B"', '"A" -> "C"'):
            self.assertIn(edge, out)

    def test_real_repo_graph(self):
        """Граф из crates.io (ответы подменяются)."""
        with mock.patch(FETCH, lambda repo, name: FAKE_CRATES[name]):
            code, out, _ = run_main([helpers.write_temp(self, REAL_CONFIG)])
        self.assertEqual(code, 0)
        self.assertIn('    "serde" -> "serde_core";\n', out)

    def test_repository_error(self):
        """Ошибка репозитория: код 1 и сообщение в stderr."""
        code, out, err = run_main([make_test_config(self, "A: B")])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("ошибка репозитория (пакет A)", err)
        self.assertIn("B не описан", err)

    def test_reverse_for_real_repo(self):
        """reverse: true без тестового репозитория: ошибка конфигурации."""
        config = helpers.write_temp(self, REAL_CONFIG + "reverse: true\n")
        code, _, err = run_main([config])
        self.assertEqual(code, 1)
        self.assertIn("ошибка конфигурации", err)

    def test_network_error(self):
        """Ошибка сети при обходе реального репозитория."""
        error = RepositoryError("не удалось подключиться к репозиторию")
        with mock.patch(FETCH, side_effect=error):
            code, _, err = run_main([helpers.write_temp(self, REAL_CONFIG)])
        self.assertEqual(code, 1)
        self.assertIn("подключиться", err)

    def test_config_error(self):
        """Ошибка конфигурации: код 1 и сообщение в stderr."""
        code, out, err = run_main(["no_such_config.yaml"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("не найден", err)


if __name__ == "__main__":
    unittest.main()
