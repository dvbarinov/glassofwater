"""
Модуль reply-клавиатур (кнопки под полем ввода).

Используется для постоянных или контекстно-зависимых кнопок,
заменяющих стандартную клавиатуру устройства.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Создаёт основную reply-клавиатуру с часто используемыми командами.

    Args:
        lang (str): Код языка (влияет на подписи кнопок).

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками /stats, /goal, /reminders.
    """
    # Пример (требует локализации текста кнопок)
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/drink"),
                KeyboardButton(text="/analyze")
            ],
            [
                KeyboardButton(text="/goal"),
                KeyboardButton(text="/reminders")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
