from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.queries import get_user, toggle_notifications
from utils.i18n import get_text, get_user_language

router = Router()


@router.message(F.text == "/reminders")
async def cmd_reminders(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        lang = get_user_language(None, message.from_user.language_code or "en")
        no_profile = get_text("reminders.no_profile", lang)
        await message.answer(no_profile)
        return

    lang = get_user_language(user["language"], message.from_user.language_code or "en")
    is_enabled = bool(user["notifications_enabled"])

    status = get_text("reminders.enabled" if is_enabled else "reminders.disabled", lang)
    btn_text = get_text("reminders.turn_off" if is_enabled else "reminders.turn_on", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="toggle_reminders")]
    ])

    await message.answer(
        get_text("reminders.status", lang, status=status),
        reply_markup=keyboard
    )


@router.callback_query(F.data == "toggle_reminders")
async def toggle_reminders_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    if not user:
        await callback.answer("⚠️ Profile not set up.", show_alert=True)
        return

    # Переключаем статус
    new_state = not bool(user["notifications_enabled"])
    await toggle_notifications(user_id, new_state)

    lang = get_user_language(user["language"], callback.from_user.language_code or "en")
    status = get_text("reminders.enabled" if new_state else "reminders.disabled", lang)

    btn_text = get_text("reminders.turn_off" if new_state else "reminders.turn_on", lang)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_text, callback_data="toggle_reminders")]
    ])

    await callback.message.edit_text(
        get_text("reminders.status", lang, status=status),
        reply_markup=keyboard
    )
    await callback.answer()
