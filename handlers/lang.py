from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.queries import set_user_language
from utils.i18n import get_text, SUPPORTED_LANGUAGES

router = Router()


async def get_lang_buttons(current_lang: str) -> list[list[InlineKeyboardButton]]:
    buttons = []
    for lang_code in SUPPORTED_LANGUAGES:
        flag = {"en": "🇬🇧", "ru": "🇷🇺", "de": "🇩🇪", "zh": "🇨🇳", "be": "🇧🇾"}.get(lang_code, "🌐")
        text = f"{flag} {SUPPORTED_LANGUAGES[lang_code]}"
        if lang_code == current_lang:
            text += " ✅"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_lang_{lang_code}")])
    return buttons


@router.message(F.text == "/lang")
async def cmd_lang(message: Message, user_lang: str):
    buttons = await get_lang_buttons(user_lang)

    await message.answer(
        get_text("lang.choose", user_lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, user_lang: str):
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
    buttons = await get_lang_buttons(user_lang)

    await callback.message.edit_text(
        get_text("lang.choose", user_lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()
