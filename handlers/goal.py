from aiogram import Router, F
from aiogram.types import Message
from database.queries import set_user_goal
from utils.i18n import get_text

router = Router()


@router.message(F.text == "/goal")
async def cmd_goal_help(message: Message, lang: str):
    """Показывает подсказку по команде /goal"""
    help_text = get_text("goal.help", lang)
    await message.answer(help_text)


@router.message(F.text.regexp(r"^/goal\s+(\d+)$"))
async def cmd_goal_set(message: Message, lang: str):
    """Обработка команды: /goal 2500"""
    try:
        goal_ml = int(message.text.split(maxsplit=1)[1])
    except (ValueError, IndexError):
        return

    if not (500 <= goal_ml <= 5000):
        error_msg = get_text("goal.invalid", lang)
        await message.answer(error_msg)
        return

    # Обновляем цель в БД
    await set_user_goal(message.from_user.id, goal_ml)

    success_msg = get_text("goal.set", lang, goal=goal_ml)
    await message.answer(success_msg)
