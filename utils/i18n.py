"""
Модуль локализации (i18n).

Обеспечивает загрузку переводов из JSON-файлов, определение языка пользователя
и поддержку hot-reload при изменении файлов. Включает автоматическую генерацию
шаблонов недостающих ключей в режиме разработки.
"""
import json
import os
from typing import Dict

from database.queries import get_user

# Поддерживаемые языки (должны совпадать с именами файлов в locales/)
SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "de": "Deutsch",
    "zh": "中国",
    "be": "Беларуская"
}
"""Список поддерживаемых языков (коды ISO 639-1)."""

_locales: Dict[str, Dict[str, str]] = {}
"""Кэш загруженных переводов по языкам."""

_last_modified: Dict[str, float] = {}
"""Время последней модификации файлов локалей (для hot-reload)."""

AUTO_GENERATE_MISSING = os.getenv("I18N_AUTO_GENERATE", "1") == "1"
"""Флаг автоматической генерации недостающих ключей (включено по умолчанию)."""


def _get_file_mtime(lang: str) -> float:
    """Возвращает время последней модификации файла локали."""
    path = f"locales/{lang}.json"
    if not os.path.exists(path):
        return 0.0
    return os.path.getmtime(path)


def _ensure_locale_file(lang: str):
    """Создаёт файл локали, если он отсутствует."""
    os.makedirs("locales", exist_ok=True)
    path = f"locales/{lang}.json"
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def _reload_locale_if_changed(lang: str):
    """
    Перезагружает локаль, если файл был изменён с момента последней загрузки.

    Args:
        lang (str): Код языка (например, 'en', 'ru').
    """
    current_mtime = _get_file_mtime(lang)
    last_mtime = _last_modified.get(lang, 0.0)

    if current_mtime > last_mtime:
        path = f"locales/{lang}.json"
        try:
            with open(path, encoding="utf-8") as f:
                _locales[lang] = json.load(f)
            _last_modified[lang] = current_mtime
        except (OSError, IOError) as e:
            # Ошибки файловой системы: файл не найден, нет прав, диск недоступен
            print(f"❌ Failed to read locale file {path}: {e}")
            if lang not in _locales:
                _locales[lang] = {}
        except json.JSONDecodeError as e:
            # Некорректный JSON: синтаксическая ошибка, незакрытая скобка и т.д.
            print(f"❌ Invalid JSON in {path}: {e}")
            if lang not in _locales:
                _locales[lang] = {}
        except UnicodeDecodeError as e:
            # Проблема с кодировкой (хотя мы явно указали utf-8)
            print(f"❌ Encoding error in {path}: {e}")
            if lang not in _locales:
                _locales[lang] = {}


def _add_missing_key_to_all(key: str):
    """
    Добавляет недостающий ключ во все файлы локалей с заглушкой.

    Args:
        key (str): Ключ перевода, отсутствующий в файлах.
    """
    for lang in SUPPORTED_LANGUAGES:
        _ensure_locale_file(lang)
        path = f"locales/{lang}.json"

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            # Восстанавливаемся "тихо": используем пустой словарь
            data = {}

        if key not in data:
            data[key] = f"MISSING: {key}"
            data = dict(sorted(data.items()))
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"🆕 Added missing key to {lang}.json: {key}")


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

async def get_user_language(user: dict | None, user_id: int, telegram_lang: str = "ru") -> str:
    """
    Определяет финальный язык интерфейса с учётом приоритетов.

    Приоритет:
        1. Язык, сохранённый в БД пользователем
        2. Язык интерфейса Telegram
        3. Английский (fallback)

    Args:
        user_db_lang (str | None): Язык из базы данных.
        telegram_lang (str): Язык из Telegram (language_code).

    Returns:
        str: Код выбранного языка.
    """
    # Получаем данные пользователя из БД
    if not user:
        user = await get_user(user_id)
    user_db_lang = user["language"] if user else None

    # Определяем финальный язык
    if user_db_lang in SUPPORTED_LANGUAGES:
        return user_db_lang
    if telegram_lang in SUPPORTED_LANGUAGES:
        return telegram_lang
    return "ru"


def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Возвращает перевод по ключу с поддержкой форматирования и hot-reload.

    Args:
        key (str): Ключ перевода (например, 'start.greeting').
        lang (str): Код языка. По умолчанию 'en'.
        **kwargs: Параметры для форматирования строки (например, current=1200).

    Returns:
        str: Отформатированная строка перевода или заглушка при отсутствии ключа.

    Примечание:
        В режиме разработки автоматически добавляет недостающие ключи во все языки.
    """
    _reload_locale_if_changed(lang)

    locale = _locales.get(lang, {})

    if key in locale:
        text = locale[key]
    else:
        text = f"{{{key}}}"
        if AUTO_GENERATE_MISSING:
            _add_missing_key_to_all(key)
            _reload_locale_if_changed(lang)
            locale = _locales.get(lang, {})
            text = locale.get(key, text)

    return text.format(**kwargs)


def get_loc_list(key: str, lang: str = "ru") -> list[str]:
    """
    Возвращает список переводов по ключу с поддержкой форматирования и hot-reload.

    Args:
        key (str): Ключ перевода (например, 'start.greeting').
        lang (str): Код языка. По умолчанию 'en'.
        **kwargs: Параметры для форматирования строки (например, current=1200).

    Returns:
        list [str]: Отформатированные строки перевода.
    """
    locale = _locales.get(lang, _locales["ru"])
    return locale.get(key).split(",")
