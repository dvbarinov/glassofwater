"""
Хэндлеры для управления умными напоминаниями о потреблении воды.

Модуль реализует интерактивное переключение напоминаний,
которые срабатывают через 2 часа после последнего приёма воды
(с учётом дневного времени: 9:00–21:00).

При отключении напоминаний автоматически отменяется
текущая запланированная задача. Все текстовые элементы локализованы.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.queries import toggle_notifications
from services.reminder_manager import cancel_reminder
from utils.i18n import get_text

router = Router()


@router.message(F.text == "/reminder")
async def cmd_reminders(message: Message, user_lang: str, user: dict | None):
    """
    Отображает текущий статус напоминаний и кнопку переключения.

    Если профиль не настроен — предлагает выполнить /start.
    Иначе показывает включены ли напоминания и даёт возможность изменить.

    Args:
        message (Message): Входящее сообщение (команда или кнопка).
        user_lang (str): Код языка, определённый middleware.
        user (dict | None): Данные пользователя из базы данных.
    """
    if not user:
        no_profile = get_text("reminders.no_profile", user_lang)
        await message.answer(no_profile)
        return

    is_enabled = bool(user["notifications_enabled"])

    status = get_text("reminders.enabled" if is_enabled else "reminders.disabled", user_lang)
    btn_text = get_text("reminders.turn_off" if is_enabled else "reminders.turn_on", user_lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="toggle_reminders")]
    ])

    await message.answer(
        get_text("reminders.status", user_lang, status=status),
        reply_markup=keyboard
    )


@router.callback_query(F.data == "toggle_reminders")
async def toggle_reminders_callback(callback: CallbackQuery, user_lang: str, user: dict | None):
    """
    Обрабатывает переключение напоминаний через inline-кнопку.

    Выполняет:
      - Обновление флага `notifications_enabled` в БД
      - Отмену текущей задачи напоминания (если отключено)
      - Отправку обновлённого статуса с новой клавиатурой

    Args:
        callback (CallbackQuery): Событие нажатия кнопки переключения.
        user_lang (str): Код языка для локализации ответа.
        user (dict | None): Данные пользователя.
    """
    user_id = callback.from_user.id

    if not user:
        await callback.answer("⚠️ Profile not set up.", show_alert=True)
        return

    # Переключаем статус
    new_state = not bool(user["notifications_enabled"])
    await toggle_notifications(user_id, new_state)

    if not new_state:
        cancel_reminder(user_id)

    status = get_text("reminders.enabled" if new_state else "reminders.disabled", user_lang)

    btn_text = get_text("reminders.turn_off" if new_state else "reminders.turn_on", user_lang)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="toggle_reminders")]
    ])

    await callback.message.edit_text(
        get_text("reminders.status", user_lang, status=status),
        reply_markup=keyboard
    )
    await callback.answer()
