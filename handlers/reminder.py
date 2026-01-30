from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.queries import toggle_notifications
from utils.i18n import get_text

router = Router()


@router.message(F.text == "/reminder")
async def cmd_reminders(message: Message, user_lang: str, user: dict | None):
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
    user_id = callback.from_user.id

    if not user:
        await callback.answer("⚠️ Profile not set up.", show_alert=True)
        return

    # Переключаем статус
    new_state = not bool(user["notifications_enabled"])
    await toggle_notifications(user_id, new_state)

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
