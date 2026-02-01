"""
Модуль inline-клавиатур (встроенных кнопок под сообщением).

Предоставляет функции для создания интерактивных кнопок,
используемых в сценариях настройки профиля, добавления воды,
управления напоминаниями и выбора языка.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.i18n import get_text, SUPPORTED_LANGUAGES


def get_gender_keyboard(user_lang: str) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора пола при настройке профиля.

    Args:
        lang (str): Код языка для локализации подписей кнопок.

    Returns:
        InlineKeyboardMarkup: Клавиатура с двумя кнопками: "Мужской" и "Женский".
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("gender.male", user_lang),
                callback_data="male"
            ),
            InlineKeyboardButton(
                text=get_text("gender.female", user_lang),
                callback_data="female"
            )
        ]
    ])


def get_activity_keyboard(user_lang: str) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора уровня физической активности.

    Args:
        lang (str): Код языка для локализации описаний.

    Returns:
        InlineKeyboardMarkup: Вертикальная клавиатура с тремя вариантами активности.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text("activity.low", user_lang), callback_data="low")],
        [InlineKeyboardButton(text=get_text("activity.medium", user_lang), callback_data="medium")],
        [InlineKeyboardButton(text=get_text("activity.high", user_lang), callback_data="high")]
    ])


def get_main_menu_keyboard(user_lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру главного меню с основными действиями.

    Включает кнопку «Сменить язык» и может быть расширена
    для других настроек (единицы измерения, цель и т.д.).

    Args:
        lang (str): Код языка для локализации подписей.

    Returns:
        InlineKeyboardMarkup: Клавиатура с одной кнопкой «🌐 Сменить язык».
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("menu.change_language", user_lang),
                callback_data="open_lang_menu"
            )
        ]
    ])


def get_drink_quick_buttons() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру быстрого добавления воды (100, 200, 300, 500 мл).

    Args:
        lang (str): Код языка (не влияет на числа, но сохраняет единообразие).

    Returns:
        InlineKeyboardMarkup: Сетка из 2×2 кнопок с объёмами в миллилитрах.
    """
    amounts = [100, 200, 300, 500]
    buttons = [
        [
            InlineKeyboardButton(
                text=f"+{amt} мл",
                callback_data=f"drink_{amt}"
            )
            for amt in amounts[:2]
        ],
        [
            InlineKeyboardButton(
                text=f"+{amt} мл",
                callback_data=f"drink_{amt}"
            )
            for amt in amounts[2:]
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lang_buttons(lang: str = "en") -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру для выбора языка интерфейса.

    Генерирует кнопки для всех поддерживаемых языков с национальными флагами.
    Текущий язык (переданный в параметре `lang`) помечается эмодзи ✅.

    Args:
        lang (str): Код текущего языка (например, 'ru', 'en').
                    Используется для отметки активного выбора.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками вида:
            - 🇬🇧 English ✅
            - 🇷🇺 Русский

    Пример использования:
        >>> kb = get_lang_buttons("ru")
        # Кнопка "🇷🇺 Русский" будет содержать "✅"
    """
    buttons = []
    for lang_code in SUPPORTED_LANGUAGES:
        flag = {"en": "🇬🇧", "ru": "🇷🇺", "de": "🇩🇪", "zh": "🇨🇳", "be": "🇧🇾"}.get(lang_code, "🌐")
        text = f"{flag} {SUPPORTED_LANGUAGES[lang_code]}"
        if lang_code == lang:
            text += " ✅"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_lang_{lang_code}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)