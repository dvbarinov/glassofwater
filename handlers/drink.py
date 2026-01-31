from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from database.queries import get_user, add_intake
from keyboards.inline import get_drink_quick_buttons
from services.reminder_manager import schedule_next_reminder
from utils.i18n import get_text, get_user_language

router = Router()


@router.message(F.text == "/drink")
async def cmd_drink_help(message: Message, user_lang: str):
    """Показывает подсказку по команде /drink"""
    help_text = get_text("drink.help", user_lang)
    await message.answer(help_text, reply_markup=get_drink_quick_buttons(user_lang))


@router.message(F.text.regexp(r"^/drink\s+(\d+)$"))
async def cmd_drink_with_amount(message: Message, user_lang: str):
    """Обработка команды вида: /drink 250"""
    amount_str = message.text.split(maxsplit=1)[1]
    await process_water_amount(message, user_lang, amount_str)


@router.message(F.text.regexp(r"^\d+$"))
async def handle_raw_number(message: Message, user_lang: str):
    """Обработка простого числа: "300" → добавить 300 мл"""
    await process_water_amount(message, user_lang, message.text)


@router.callback_query(F.data.startswith("drink_"))
async def drink_callback(callback: CallbackQuery, user_lang: str):
    """Обработка inline-кнопок: drink_200, drink_500 и т.д."""
    try:
        amount = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        await add_intake(user_id, amount)

        success_msg = get_text("drink.added", user_lang, amount=amount)
        await callback.message.edit_text(success_msg)
        await callback.answer()
    except (ValueError, IndexError):
        await callback.answer("❌ Некорректные данные", show_alert=True)


async def process_water_amount(message: Message, user_lang: str, user: dict | None, amount_str: str, bot: Bot):
    """Общая логика обработки объёма воды"""
    try:
        amount = int(amount_str)
    except ValueError:
        return  # Игнорируем нечисловые значения

    if not (50 <= amount <= 3000):
        error_msg = get_text("drink.invalid_amount", user_lang)
        await message.answer(error_msg)
        return

    await add_intake(message.from_user.id, amount)

    if user and user["notifications_enabled"]:
        schedule_next_reminder(bot, message.from_user.id, minutes=100)

    # Получаем цель для расчёта прогресса
    user = await get_user(message.from_user.id)

    if user and user["daily_goal_ml"]:
        today_total = await get_today_total(message.from_user.id)  # потребуется реализация
        percent = min(100, round(today_total / user["daily_goal_ml"] * 100))
        success_msg = get_text("drink.added_with_progress", user_lang, amount=amount, current=today_total,
                               goal=user["daily_goal_ml"], percent=percent)
    else:
        success_msg = get_text("drink.added", user_lang, amount=amount)

    await message.answer(success_msg, reply_markup=get_drink_quick_buttons(user_lang))


# --- Вспомогательная функция (временно здесь, позже можно вынести в queries.py) ---
async def get_today_total(user_id: int) -> int:
    """Возвращает сумму воды за сегодня в мл"""
    from datetime import datetime, timezone
    from sqlalchemy import select, func
    from database.engine import AsyncSessionLocal
    from database.models import intakes

    today = datetime.now(timezone.utc).date()
    async with AsyncSessionLocal() as session:
        query = (
            select(func.sum(intakes.c.amount_ml))
            .where(intakes.c.user_id == user_id)
            .where(func.date(intakes.c.timestamp) == today)
        )
        result = await session.execute(query)
        total = result.scalar()
        return total or 0
