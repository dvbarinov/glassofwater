# tests/test_i18n.py
import unittest
import os
import json
from utils.i18n import get_text, get_user_language

class TestI18n(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаём временные файлы локалей
        os.makedirs("locales", exist_ok=True)
        with open("locales/en.json", "w") as f:
            json.dump({"test.hello": "Hello, {name}!"}, f)
        with open("locales/ru.json", "w") as f:
            json.dump({"test.hello": "Привет, {name}!"}, f)

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы
        for lang in ["en", "ru"]:
            try:
                os.remove(f"locales/{lang}.json")
            except:
                pass

    def test_get_text_en(self):
        result = get_text("test.hello", "en", name="Alice")
        self.assertEqual(result, "Hello, Alice!")

    def test_get_text_ru(self):
        result = get_text("test.hello", "ru", name="Алиса")
        self.assertEqual(result, "Привет, Алиса!")

    def test_missing_key(self):
        result = get_text("non.existent", "en")
        self.assertEqual(result, "MISSING: non.existent")

if __name__ == '__main__':
    unittest.main()