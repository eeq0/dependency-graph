"""Тесты запуска приложения."""
import contextlib
import io
import unittest

import helpers
from main import main


def run_main(argv):
    """Запустить main и вернуть (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Вывод параметров и ошибок."""

    def test_prints_key_value(self):
        """Все параметры выводятся в формате «ключ = значение»."""
        path = helpers.write_temp(
            self, "package: serde\nrepository: https://crates.io\n"
                  "test_mode: false\n")
        code, out, _ = run_main([path])
        self.assertEqual(code, 0)
        self.assertEqual(out, "package = serde\n"
                              "repository = https://crates.io\n"
                              "test_mode = false\n")

    def test_error_exit_code(self):
        """При ошибке код 1 и сообщение в stderr."""
        code, out, err = run_main(["no_such_config.yaml"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("не найден", err)


if __name__ == "__main__":
    unittest.main()
