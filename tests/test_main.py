"""Тесты запуска приложения."""
import contextlib
import io
import unittest
from unittest import mock

import helpers
from errors import RepositoryError
from main import main

CONFIG = "package: serde\nrepository: https://crates.io\ntest_mode: false\n"
FETCH = "main.get_direct_dependencies"


def run_main(argv):
    """Запустить main и вернуть (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Вывод зависимостей и ошибок."""

    def test_prints_dependencies(self):
        """Выводятся все прямые зависимости, отсортированные по имени."""
        deps = {"serde_derive": ("^1", True), "serde_core": ("=1.0", False)}
        with mock.patch(FETCH, return_value=("1.0", deps)):
            code, out, _ = run_main([helpers.write_temp(self, CONFIG)])
        self.assertEqual(code, 0)
        self.assertEqual(out, "Прямые зависимости пакета serde 1.0:\n"
                              "  serde_core =1.0\n"
                              "  serde_derive ^1 (необязательная)\n")

    def test_no_dependencies(self):
        """Пакет без зависимостей."""
        with mock.patch(FETCH, return_value=("1.0", {})):
            _, out, _ = run_main([helpers.write_temp(self, CONFIG)])
        self.assertIn("нет зависимостей", out)

    def test_repository_error(self):
        """Ошибка репозитория: код 1 и сообщение в stderr."""
        error = RepositoryError("пакет не найден в репозитории: ...")
        with mock.patch(FETCH, side_effect=error):
            code, out, err = run_main([helpers.write_temp(self, CONFIG)])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("ошибка репозитория (пакет serde)", err)

    def test_test_mode_not_ready(self):
        """Тестовый репозиторий пока не поддерживается (этап 3)."""
        repo = helpers.write_temp(self, "A: B\n", ".txt")
        config = f"package: A\nrepository: {repo}\ntest_mode: true\n"
        code, _, err = run_main([helpers.write_temp(self, config)])
        self.assertEqual(code, 1)
        self.assertIn("этапе 3", err)

    def test_config_error(self):
        """Ошибка конфигурации: код 1 и сообщение в stderr."""
        code, out, err = run_main(["no_such_config.yaml"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("не найден", err)


if __name__ == "__main__":
    unittest.main()
