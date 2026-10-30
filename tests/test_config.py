"""Тесты чтения YAML и проверки параметров."""
import unittest

import helpers
from config import load_config, validate
from errors import ConfigError
from yaml_reader import parse_yaml

GOOD = {"package": "serde", "repository": "https://crates.io",
        "test_mode": False}


class YamlTest(unittest.TestCase):
    """Разбор YAML."""

    def test_values_comments_and_quotes(self):
        """Строки, true/false, кавычки и комментарии."""
        text = "# конфиг\npackage: 'serde'  # имя\ntest_mode: true\n"
        self.assertEqual(parse_yaml(text),
                         {"package": "serde", "test_mode": True})

    def test_syntax_errors(self):
        """Нет двоеточия, повтор ключа, вложенность, незакрытая кавычка."""
        for text in ("package serde", "a: 1\na: 2", "a:\n  b: 1",
                     "a: 'open"):
            with self.assertRaises(ConfigError, msg=text):
                parse_yaml(text)


class ValidateTest(unittest.TestCase):
    """Проверка параметров."""

    def test_good_config(self):
        """Правильная конфигурация без ошибок."""
        self.assertEqual(validate(GOOD), [])

    def test_each_parameter_error(self):
        """Для каждого параметра есть своя ошибка."""
        cases = {
            "package": {"package": "1 bad"},
            "repository": {"repository": "crates.io"},
            "test_mode": {"test_mode": "maybe"},
        }
        for name, change in cases.items():
            errors = validate({**GOOD, **change})
            self.assertEqual(len(errors), 1, name)
            self.assertTrue(errors[0].startswith(name), errors)

    def test_missing_and_unknown(self):
        """Пропущенный и лишний параметры."""
        errors = validate({"package": "serde", "depth": "3"})
        self.assertEqual(len(errors), 3)

    def test_reverse(self):
        """reverse: только true/false и только для тестового репозитория."""
        path = helpers.write_temp(self, "A:\n", suffix=".txt")
        test = {"package": "A", "repository": path, "test_mode": True}
        self.assertEqual(validate({**test, "reverse": True}), [])
        self.assertEqual(len(validate({**test, "reverse": "yes"})), 1)
        errors = validate({**GOOD, "reverse": True})
        self.assertEqual(len(errors), 1)
        self.assertIn("test_mode: true", errors[0])

    def test_test_mode_needs_existing_file(self):
        """В тестовом режиме repository должен быть файлом."""
        path = helpers.write_temp(self, "A: B\n", suffix=".txt")
        good = {"package": "A", "repository": path, "test_mode": True}
        self.assertEqual(validate(good), [])
        missing = {**good, "repository": path + ".none"}
        self.assertEqual(len(validate(missing)), 1)


class LoadConfigTest(unittest.TestCase):
    """Загрузка конфигурации из файла."""

    def test_load(self):
        """Файл читается, reverse по умолчанию false."""
        path = helpers.write_temp(
            self, "test_mode: false\nrepository: https://crates.io\n"
                  "package: serde\n")
        self.assertEqual(load_config(path),
                         {"package": "serde",
                          "repository": "https://crates.io",
                          "test_mode": False, "reverse": False})

    def test_missing_file(self):
        """Нет файла: понятная ошибка."""
        with self.assertRaises(ConfigError):
            load_config("no_such_config.yaml")


if __name__ == "__main__":
    unittest.main()
