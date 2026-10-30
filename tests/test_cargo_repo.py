"""Тесты получения прямых зависимостей (сеть подменяется)."""
import io
import unittest
import urllib.error
from unittest import mock

import helpers
from cargo_repo import get_direct_dependencies, parse_dependencies
from errors import RepositoryError

REPO = "https://crates.io"
URLOPEN = "cargo_repo.urllib.request.urlopen"
CRATE = {"crate": {"max_stable_version": "1.0.0", "max_version": "1.1.0-rc"}}
DEPS = {"dependencies": [
    {"crate_id": "serde_core", "req": "=1.0.0", "kind": "normal",
     "optional": False},
    {"crate_id": "serde_derive", "req": "^1", "kind": "normal",
     "optional": True},
    {"crate_id": "trybuild", "req": "^1", "kind": "dev", "optional": False},
    {"crate_id": "serde_core", "req": "^1", "kind": "build",
     "optional": False},
]}


class ParseTest(unittest.TestCase):
    """Разбор ответа API."""

    def test_skips_dev_and_repeats(self):
        """dev-зависимости и повторы имён не попадают в результат."""
        self.assertEqual(parse_dependencies(DEPS),
                         {"serde_core": ("=1.0.0", False),
                          "serde_derive": ("^1", True)})

    def test_bad_answer(self):
        """Ответ без нужных полей даёт RepositoryError."""
        for data in ({}, {"dependencies": [{"name": "x"}]}, []):
            with self.assertRaises(RepositoryError, msg=data):
                parse_dependencies(data)


class FetchTest(unittest.TestCase):
    """Обращение к репозиторию."""

    def test_two_requests(self):
        """Сначала версия пакета, затем её зависимости."""
        with mock.patch(URLOPEN,
                        side_effect=[helpers.answer(CRATE),
                                     helpers.answer(DEPS)]) as fake:
            version, deps = get_direct_dependencies(REPO + "/", "serde")
        self.assertEqual(version, "1.0.0")
        self.assertEqual(set(deps), {"serde_core", "serde_derive"})
        urls = [call.args[0].full_url for call in fake.call_args_list]
        self.assertEqual(urls, [
            REPO + "/api/v1/crates/serde",
            REPO + "/api/v1/crates/serde/1.0.0/dependencies"])

    def test_package_not_found(self):
        """Ответ 404 означает, что такого пакета нет."""
        error = urllib.error.HTTPError(REPO, 404, "Not Found", None, None)
        with mock.patch(URLOPEN, side_effect=error):
            with self.assertRaisesRegex(RepositoryError, "не найден"):
                get_direct_dependencies(REPO, "no-such-crate")

    def test_no_connection(self):
        """Нет сети или неверный адрес сервера."""
        error = urllib.error.URLError("host not found")
        with mock.patch(URLOPEN, side_effect=error):
            with self.assertRaisesRegex(RepositoryError, "подключиться"):
                get_direct_dependencies(REPO, "serde")

    def test_not_json(self):
        """Сервер ответил не JSON (например, это не репозиторий)."""
        page = io.BytesIO(b"<html>hello</html>")
        with mock.patch(URLOPEN, return_value=page):
            with self.assertRaisesRegex(RepositoryError, "не JSON"):
                get_direct_dependencies(REPO, "serde")


if __name__ == "__main__":
    unittest.main()
