import asyncio
from datetime import datetime, time, timezone
import pytz
from typing import Dict, Optional

from aiogram import Bot
from database.queries import get_user
from keyboards.inline import get_drink_quick_buttons
from utils.i18n import get_text, get_user_language

# Хранилище активных задач: {user_id: Task}
_active_reminders: Dict[int, asyncio.Task] = {}

def cancel_reminder(user_id: int):
    """Отменяет текущее напоминание для пользователя"""
    if user_id in _active_reminders:
        _active_reminders[user_id].cancel()
        del _active_reminders[user_id]

async def _send_reminder(bot: Bot, user_id: int):
    """Отправляет напоминание пользователю"""
    try:
        user = await get_user(user_id)
        if not user or not user["notifications_enabled"]:
            return

        # Проверка времени (локального)
        tz_offset = user.get("timezone_offset", 0)  # в минутах
        user_tz = pytz.FixedOffset(tz_offset)
        now_local = datetime.now(timezone.utc).astimezone(user_tz).time()

        if not (time(9, 0) <= now_local <= time(21, 0)):
            # Вне рабочих часов — откладываем на 9:00 следующего дня
            delay = _get_delay_to_next_morning(tz_offset)
            _schedule_reminder(bot, user_id, delay)
            return

        # Отправляем напоминание
        lang = get_user_language(user["language"], "en")
        msg = get_text("reminders.notification", lang)
        await bot.send_message(
            chat_id=user_id,
            text=msg,
            reply_markup=get_drink_quick_buttons(lang)
        )

    except Exception as e:
        print(f"Ошибка отправки напоминания {user_id}: {e}")

def _get_delay_to_next_morning(tz_offset: int) -> float:
    """Возвращает задержку до 9:00 следующего дня в секундах"""
    from datetime import datetime, timedelta, timezone
    now_utc = datetime.now(timezone.utc)
    user_tz = pytz.FixedOffset(tz_offset)
    now_local = now_utc.astimezone(user_tz)
    next_morning = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
    if now_local.time() >= time(9, 0):
        next_morning += timedelta(days=1)
    delay = (next_morning - now_local).total_seconds()
    return max(delay, 60)  # минимум 1 минута

def _schedule_reminder(bot: Bot, user_id: int, delay: float):
    """Планирует напоминание через delay секунд"""
    async def wrapper():
        await asyncio.sleep(delay)
        await _send_reminder(bot, user_id)

    task = asyncio.create_task(wrapper())
    _active_reminders[user_id] = task

def schedule_next_reminder(bot: Bot, user_id: int, minutes: int = 120):
    """
    Планирует напоминание через `hours` часов.
    Автоматически отменяет предыдущее.
    """
    cancel_reminder(user_id)
    delay_seconds = minutes * 60
    _schedule_reminder(bot, user_id, delay_seconds)