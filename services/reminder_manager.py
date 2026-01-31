"""
Модуль управления динамическими напоминаниями о потреблении воды.

Реализует умные напоминания, которые срабатывают через заданный интервал
после последнего приёма воды, с учётом дневного времени (9:00–21:00)
и часового пояса пользователя.
"""

import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import Dict
import logging
import pytz

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from database.queries import get_user, toggle_notifications
from keyboards.inline import get_drink_quick_buttons
from utils.i18n import get_text, get_user_language


_active_reminders: Dict[int, asyncio.Task] = {}
"""Глобальное хранилище активных задач напоминаний по user_id."""


def cancel_reminder(user_id: int) -> None:
    """
    Отменяет текущее напоминание для пользователя.

    Args:
        user_id (int): Telegram ID пользователя.
    """
    if user_id in _active_reminders:
        _active_reminders[user_id].cancel()
        del _active_reminders[user_id]


async def _send_reminder(bot: Bot, user_id: int) -> None:
    """
    Отправляет напоминание пользователю о необходимости выпить воды.

    Проверяет:
        - Включены ли напоминания у пользователя
        - Находится ли локальное время в диапазоне 9:00–21:00
        - Если вне диапазона — переносит напоминание на 9:00 следующего дня

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
        user_id (int): Telegram ID получателя.
    """
    try:
        user = await get_user(user_id)
        if not user or not user.get("notifications_enabled"):
            return

        # Определяем локальное время пользователя
        tz_offset = user.get("timezone_offset", 0)  # в минутах от UTC
        user_tz = pytz.FixedOffset(tz_offset)
        now_local = datetime.now(timezone.utc).astimezone(user_tz).time()

        # Проверка рабочих часов
        if not time(9, 0) <= now_local <= time(21, 0):
            delay = _get_delay_to_next_morning(tz_offset)
            _schedule_reminder(bot, user_id, delay)
            return

        # Отправка напоминания
        lang = get_user_language(user.get("language"), "en")
        msg = get_text("reminders.notification", lang)
        await bot.send_message(
            chat_id=user_id,
            text=msg,
            reply_markup=get_drink_quick_buttons(lang)
        )

    except TelegramAPIError as e:
        # Ожидаемые ошибки Telegram: пользователь заблокировал, чат не найден и т.д.
        print(f"⚠️ Не удалось отправить напоминание пользователю {user_id}: {e}")
        # Опционально: отключить напоминания для этого пользователя
        await toggle_notifications(user_id, False)
    except (OSError, asyncio.TimeoutError) as e:
        # Сетевые проблемы — можно повторить или проигнорировать
        print(f"🌐 Сетевая ошибка при отправке напоминания {user_id}: {e}")
    except Exception as e:
        # Только для непредвиденных ошибок (баги в коде)
        # В продакшене лучше логировать
        logging.exception("❌ Критическая ошибка в _send_reminder для %s", user_id)
        raise  # Перебрасываем, чтобы не скрывать баги


def _get_delay_to_next_morning(tz_offset: int) -> float:
    """
    Вычисляет задержку до 9:00 следующего дня в секундах.

    Args:
        tz_offset (int): Смещение часового пояса в минутах от UTC.

    Returns:
        float: Задержка в секундах (минимум 60 сек).
    """
    now_utc = datetime.now(timezone.utc)
    user_tz = pytz.FixedOffset(tz_offset)
    now_local = now_utc.astimezone(user_tz)
    next_morning = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
    if now_local.time() >= time(9, 0):
        next_morning += timedelta(days=1)
    delay = (next_morning - now_local).total_seconds()
    return max(delay, 60)


def _schedule_reminder(bot: Bot, user_id: int, delay: float) -> None:
    """
    Планирует выполнение напоминания через указанную задержку.

    Args:
        bot (Bot): Экземпляр бота.
        user_id (int): Telegram ID пользователя.
        delay (float): Задержка в секундах.
    """
    async def wrapper():
        await asyncio.sleep(delay)
        await _send_reminder(bot, user_id)

    task = asyncio.create_task(wrapper())
    _active_reminders[user_id] = task


def schedule_next_reminder(bot: Bot, user_id: int, minutes: int = 120) -> None:
    """
    Планирует новое напоминание через N часов после последнего действия.

    Автоматически отменяет предыдущее напоминание для этого пользователя.

    Args:
        bot (Bot): Экземпляр бота.
        user_id (int): Telegram ID пользователя.
        hours (int): Интервал в часах (по умолчанию 2).
    """
    cancel_reminder(user_id)
    delay_seconds = minutes * 60
    _schedule_reminder(bot, user_id, delay_seconds)
