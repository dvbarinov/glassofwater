# keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Мужской 👨", callback_data="male"),
            InlineKeyboardButton(text="Женский 👩", callback_data="female")
        ]
    ])

def get_activity_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Низкая (сидячий образ жизни)", callback_data="low")],
        [InlineKeyboardButton(text="Средняя (лёгкие тренировки 1–3 раза/неделю)", callback_data="medium")],
        [InlineKeyboardButton(text="Высокая (интенсивные нагрузки 4+ раз/неделю)", callback_data="high")]
    ])