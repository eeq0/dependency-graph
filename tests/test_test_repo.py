"""Тесты чтения файла тестового репозитория."""
import unittest

import helpers
from errors import RepositoryError
from test_repo import parse_test_repo, read_test_repo


class ParseTestRepoTest(unittest.TestCase):
    """Разбор описания графа."""

    def test_packages_and_comments(self):
        """Пакеты, пустые строки, комментарии и повтор зависимости."""
        text = "# граф\nA: B C B  # A\n\nB:\nC: A\n"
        self.assertEqual(parse_test_repo(text),
                         {"A": ["B", "C"], "B": [], "C": ["A"]})

    def test_errors(self):
        """Нет двоеточия, плохое имя, повтор, неописанный пакет."""
        for text in ("A B", "A: b", "a: B", ": B", "A1: B", "A:\nA: B",
                     "A: B"):
            with self.assertRaises(RepositoryError, msg=text):
                parse_test_repo(text)

    def test_read_file(self):
        """Файл читается с диска."""
        path = helpers.write_temp(self, "A: B\nB:\n", ".txt")
        self.assertEqual(read_test_repo(path), {"A": ["B"], "B": []})

    def test_missing_file(self):
        """Файла нет: RepositoryError."""
        with self.assertRaises(RepositoryError):
            read_test_repo("no_such_repo.txt")


if __name__ == "__main__":
    unittest.main()
