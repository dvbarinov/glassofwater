# utils/i18n.py
import json
import os
from typing import Dict, Optional

from database.queries import get_user

# Поддерживаемые языки (должны совпадать с именами файлов в locales/)
SUPPORTED_LANGUAGES = ["ru", "en"]
_locales: Dict[str, Dict[str, str]] = {}

def load_locales():
    for lang in SUPPORTED_LANGUAGES:
        path = f"locales/{lang}.json"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                _locales[lang] = json.load(f)
        else:
            _locales[lang] = {}
# def load_locales():
#     for filename in os.listdir("locales"):
#         if filename.endswith(".json"):
#             lang = filename[:-5]  # "ru.json" → "ru"
#             with open(f"locales/{filename}", encoding="utf-8") as f:
#                 _locales[lang] = json.load(f)

async def get_user_language(user_id: int, telegram_lang: str = "ru") -> str:
    """Определяет язык с приоритетом: БД → Telegram → en"""
    user = await get_user(user_id)
    user_db_lang = user["language"] if user else None
    if user_db_lang in SUPPORTED_LANGUAGES:
        return user_db_lang
    if telegram_lang in SUPPORTED_LANGUAGES:
        return telegram_lang
    return "ru"

def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    locale = _locales.get(lang, _locales["ru"])
    text = locale.get(key, f"{{{key}}}")  # fallback + debug
    return text.format(**kwargs)