from aiogram import Router, F
from aiogram.types import Message
from database.queries import get_user, set_user_goal
from utils.i18n import get_text, get_user_language

router = Router()


@router.message(F.text == "/goal")
async def cmd_goal_help(message: Message):
    """Показывает подсказку по команде /goal"""
    user_lang = await get_user_language(
        message.from_user.id,
        telegram_lang=message.from_user.language_code
    )
    help_text = get_text("goal.help", user_lang)
    await message.answer(help_text)


@router.message(F.text.regexp(r"^/goal\s+(\d+)$"))
async def cmd_goal_set(message: Message):
    """Обработка команды: /goal 2500"""
    try:
        goal_ml = int(message.text.split(maxsplit=1)[1])
    except (ValueError, IndexError):
        return

    user_lang = await get_user_language(
        message.from_user.id,
        telegram_lang=message.from_user.language_code
    )

    if not (500 <= goal_ml <= 5000):
        error_msg = get_text("goal.invalid", user_lang)
        await message.answer(error_msg)
        return

    # Обновляем цель в БД
    await set_user_goal(message.from_user.id, goal_ml)

    success_msg = get_text("goal.set", user_lang, goal=goal_ml)
    await message.answer(success_msg)
