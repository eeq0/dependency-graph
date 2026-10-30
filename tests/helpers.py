"""Общие помощники для тестов: путь к src и временные файлы."""
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))


def write_temp(test, text, suffix=".yaml"):
    """Записать текст во временный файл, удаляемый после теста."""
    handle, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        file.write(text)
    test.addCleanup(os.remove, path)
    return path
