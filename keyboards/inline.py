# keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.i18n import get_text


def get_gender_keyboard(user_lang: str) -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Низкая (сидячий образ жизни)", callback_data="low")],
        [InlineKeyboardButton(text="Средняя (лёгкие тренировки 1–3 раза/неделю)", callback_data="medium")],
        [InlineKeyboardButton(text="Высокая (интенсивные нагрузки 4+ раз/неделю)", callback_data="high")]
    ])

def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Основное меню с полезными кнопками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text("menu.change_language", lang),
                callback_data="open_lang_menu"
            )
        ]
    ])

def get_drink_quick_buttons(lang: str = "en") -> InlineKeyboardMarkup:
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
