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


def make_test_config(test, repo_text, package="A"):
    """Создать файл тестового репозитория и конфигурацию для него."""
    repo = helpers.write_temp(test, repo_text, ".txt")
    return helpers.write_temp(
        test, f"package: {package}\nrepository: {repo}\ntest_mode: true\n")


class MainTest(unittest.TestCase):
    """Вывод графа и ошибок."""

    def test_test_repo_graph(self):
        """Граф тестового репозитория с циклом."""
        code, out, _ = run_main([make_test_config(self, "A: B C\nB: A\nC:")])
        self.assertEqual(code, 0)
        self.assertEqual(out, "Граф зависимостей пакета A (обход BFS):\n"
                              "  A -> B, C\n"
                              "  B -> A\n"
                              "  C -> (нет зависимостей)\n"
                              "Всего пакетов: 3\n")

    def test_real_repo_graph(self):
        """Граф из crates.io (ответы подменяются)."""
        with mock.patch(FETCH, lambda repo, name: FAKE_CRATES[name]):
            code, out, _ = run_main([helpers.write_temp(self, REAL_CONFIG)])
        self.assertEqual(code, 0)
        self.assertIn("  serde -> serde_core\n", out)
        self.assertIn("Всего пакетов: 2", out)

    def test_repository_error(self):
        """Ошибка репозитория: код 1 и сообщение в stderr."""
        code, out, err = run_main([make_test_config(self, "A: B")])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("ошибка репозитория (пакет A)", err)
        self.assertIn("B не описан", err)

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
