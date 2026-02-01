"""
Хэндлеры для управления языком интерфейса бота.

Модуль предоставляет интерактивное меню выбора языка,
сохраняет предпочтения пользователя в базе данных
и поддерживает мгновенное переключение без перезапуска.

Все текстовые элементы локализованы, включая подписи кнопок.
Поддерживаемые языки определяются в `utils/i18n.py`.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.queries import set_user_language
from keyboards.inline import get_lang_buttons
from utils.i18n import get_text, SUPPORTED_LANGUAGES

router = Router()
"""Роутер для хэндлеров, связанных с выбором языка интерфейса."""


@router.message(F.text == "/lang")
async def cmd_lang(message: Message, user_lang: str):
    """
    Открывает меню выбора языка интерфейса.

    Отображает список поддерживаемых языков с флагами.
    Текущий язык помечается эмодзи ✅.

    Args:
        message (Message): Входящее сообщение (команда /lang или кнопка).
        user_lang (str): Текущий язык пользователя (определён middleware).
        user (dict | None): Данные пользователя из БД.
    """

    await message.answer(
        get_text("lang.choose", user_lang),
        reply_markup=get_lang_buttons(user_lang)
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, user_lang: str):
    """
    Обрабатывает выбор конкретного языка.

    Извлекает код языка из callback_data (формат: "set_lang_<код>"),
    сохраняет его в профиль пользователя и отправляет подтверждение.

    Args:
        callback (CallbackQuery): Событие выбора языка.
        user_lang (str): Язык до изменения (используется для отображения подтверждения).
        user (dict | None): Данные пользователя.
    """

    lang = callback.data.split("_")[-1]
    if lang not in SUPPORTED_LANGUAGES:
        await callback.answer(
            get_text("lang.unsupported", user_lang),
            show_alert=True
        )
        return

    await set_user_language(callback.from_user.id, lang)

    # Получаем текст на новом языке
    confirmation = get_text("lang.changed", lang)
    await callback.message.edit_text(confirmation)
    await callback.answer()


@router.callback_query(F.data == "open_lang_menu")
async def open_lang_menu(callback: CallbackQuery, user_lang: str):
    """
    Открывает меню выбора языка через inline-кнопку из главного меню.

    Используется как альтернатива команде /lang — например, из клавиатуры после /start.
    Отображает поддерживаемые языки с флагами
    и помечает текущий выбор галочкой.

    Args:
        callback (CallbackQuery): Событие нажатия кнопки "🌐 Сменить язык".
        user_lang (str): Текущий язык интерфейса.
        user (dict | None): Данные пользователя.
    """

    await callback.message.edit_text(
        get_text("lang.choose", user_lang),
        reply_markup=get_lang_buttons(user_lang)
    )
    await callback.answer()
