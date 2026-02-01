"""
Хэндлеры для добавления записей о потреблении воды.

Модуль обрабатывает три способа ввода объёма воды:
  1. Команда вида `/drink <объём>` (например, `/drink 250`)
  2. Простое числовое сообщение (например, `300`)
  3. Нажатие inline-кнопок быстрого ввода (+100, +200 и т.д.)

После успешного добавления:
  - Обновляется прогресс за день
  - Планируется новое умное напоминание (через 2 часа)
  - Пользователь получает подтверждение с текущим прогрессом

Автоматически обновляет прогресс и планирует напоминания.
Все текстовые ответы локализованы через middleware.
"""

from datetime import datetime, timezone

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, func
from database.queries import get_user, add_intake
from database.engine import AsyncSessionLocal
from database.models import intakes
from keyboards.inline import get_drink_quick_buttons
from services.reminder_manager import schedule_next_reminder
from utils.i18n import get_text

router = Router()


@router.message(F.text == "/drink")
async def cmd_drink_help(message: Message, user_lang: str):
    """
    Отображает справку по команде /drink и клавиатуру быстрого ввода.

    Args:
        message (Message): Входящее сообщение с командой /drink.
        user_lang (str): Код языка, определённый middleware.
    """
    help_text = get_text("drink.help", user_lang)
    await message.answer(help_text, reply_markup=get_drink_quick_buttons(user_lang))


@router.message(F.text.regexp(r"^/drink\s+(\d+)$"))
async def cmd_drink_with_amount(message: Message, user_lang: str, user: dict | None, bot: Bot):
    """
    Обрабатывает команду /drink с указанием объёма.

    Извлекает число из сообщения, валидирует его и добавляет запись.

    Args:
        message (Message): Сообщение вида "/drink 250".
        user_lang (str): Код языка.
        user (dict | None): Данные пользователя из БД.
        bot (Bot): Экземпляр бота (внедряется aiogram).
    """
    amount_str = message.text.split(maxsplit=1)[1]
    await process_water_amount(message, user_lang, user, amount_str, bot)


@router.message(F.text.regexp(r"^\d+$"))
async def handle_raw_number(message: Message, user_lang: str, user: dict | None, bot: Bot):
    """
    Обрабатывает простое числовое сообщение как объём воды.

    Валидирует диапазон (50–3000 мл), сохраняет запись
    и обновляет прогресс пользователя.

    Args:
        message (Message): Сообщение с числом.
        user_lang (str): Код языка.
        user (dict | None): Данные пользователя.
        bot (Bot): Экземпляр бота (внедряется aiogram).
    """
    await process_water_amount(message, user_lang, user, message.text, bot)


@router.callback_query(F.data.startswith("drink_"))
async def drink_callback(callback: CallbackQuery, user_lang: str):
    """
    Обрабатывает нажатие inline-кнопок быстрого ввода.

    Callback data имеет формат: "drink_<объём>" (например, "drink_200").

    Args:
        callback (CallbackQuery): Событие нажатия кнопки.
        user_lang (str): Код языка.
        user (dict | None): Данные пользователя.
    """
    try:
        amount = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        await add_intake(user_id, amount)

        success_msg = get_text("drink.added", user_lang, amount=amount)
        await callback.message.edit_text(success_msg)
        await callback.answer()
    except (ValueError, IndexError):
        await callback.answer("❌ Некорректные данные", show_alert=True)


async def process_water_amount(
        message: Message,
        user_lang: str,
        user: dict | None,
        amount_str: str,
        bot: Bot
):
    """
    Основная логика обработки объёма воды.

    Выполняет:
      - Валидацию (50 ≤ объём ≤ 3000 мл)
      - Сохранение в БД
      - Планирование напоминания
      - Отправку подтверждения с прогрессом

    Args:
        message (Message): Исходное сообщение от пользователя.
        amount_str (str): Строка с числом (для парсинга).
        user_lang (str): Код языка.
        user (dict | None): Данные пользователя.
        bot (Bot): Экземпляр бота.
    """
    try:
        amount = int(amount_str)
    except ValueError:
        return  # Игнорируем нечисловые значения

    if not 50 <= amount <= 3000:
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
        success_msg = get_text(
            "drink.added_with_progress",
            user_lang,
            amount=amount,
            current=today_total,
            goal=user["daily_goal_ml"],
            percent=percent
        )
    else:
        success_msg = get_text("drink.added", user_lang, amount=amount)

    await message.answer(success_msg, reply_markup=get_drink_quick_buttons(user_lang))


# --- Вспомогательная функция (временно здесь, позже можно вынести в queries.py) ---
async def get_today_total(user_id: int) -> int:
    """Возвращает сумму воды за сегодня в мл"""

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
