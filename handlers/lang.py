from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.queries import get_user, set_user_language
from utils.i18n import get_text, SUPPORTED_LANGUAGES, get_user_language

router = Router()

@router.message(F.text == "/lang")
async def cmd_lang(message: Message):
    user = await get_user(message.from_user.id)
    current_lang = user["language"] if user else message.from_user.language_code or "en"
    if current_lang not in SUPPORTED_LANGUAGES:
        current_lang = "en"

    buttons = []
    for lang_code in SUPPORTED_LANGUAGES:
        flag = {"en": "🇬🇧", "ru": "🇷🇺"}.get(lang_code, "🌐")
        text = f"{flag} {'English' if lang_code == 'en' else 'Русский'}"
        if lang_code == current_lang:
            text += " ✅"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_lang_{lang_code}")])

    await message.answer(
        "Выберите язык интерфейса:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[-1]
    if lang not in SUPPORTED_LANGUAGES:
        await callback.answer("Язык не поддерживается.", show_alert=True)
        return

    await set_user_language(callback.from_user.id, lang)

    # Получаем текст на новом языке
    confirmation = get_text("lang.changed", lang)
    await callback.message.edit_text(confirmation)
    await callback.answer()

@router.callback_query(F.data == "open_lang_menu")
async def open_lang_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    user_lang = await get_user_language(
        user_id = callback.from_user.id,
        telegram_lang = callback.from_user.language_code
    )

    buttons = []
    for lang_code in SUPPORTED_LANGUAGES:
        flag = {"en": "🇬🇧", "ru": "🇷🇺"}.get(lang_code, "🌐")
        text = f"{flag} {'English' if lang_code == 'en' else 'Русский'}"
        if user and user["language"] == lang_code:
            text += " ✅"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_lang_{lang_code}")])

    await callback.message.edit_text(
        get_text("lang.choose", user_lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()