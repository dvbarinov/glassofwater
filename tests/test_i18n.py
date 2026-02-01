# tests/test_i18n.py
import os
import json
import pytest
from utils.i18n import get_text, get_user_language


@pytest.fixture(scope="module", autouse=True)
def setup_locales():
    """Создаёт временные файлы локалей перед тестами и удаляет после"""
    os.makedirs("locales", exist_ok=True)
    locales = {
        "en": {"test.hello": "Hello, {name}!"},
        "ru": {"test.hello": "Привет, {name}!"}
    }
    for lang, data in locales.items():
        with open(f"locales/{lang}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    yield  # запуск тестов

    # Очистка
    for lang in locales:
        try:
            os.remove(f"locales/{lang}.json")
        except FileNotFoundError:
            pass


def test_get_text_en():
    result = get_text("test.hello", "en", name="Alice")
    assert result == "Hello, Alice!"


def test_get_text_ru():
    result = get_text("test.hello", "ru", name="Алиса")
    assert result == "Привет, Алиса!"


def test_missing_key():
    result = get_text("non.existent", "en")
    assert result == "MISSING: non.existent"
