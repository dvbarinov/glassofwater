"""
Хэндлеры для просмотра статистики потребления воды.

Генерирует текстовый отчёт и график за последние 7 дней,
с учётом текущей цели пользователя.
"""

import os
from datetime import timedelta, datetime, timezone

from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from utils.chart import generate_weekly_chart
from utils.i18n import get_text, get_loc_list
from database.queries import get_today_intakes, get_weekly_totals

router = Router()


@router.message(F.text == "/analyze")
async def cmd_stats(message: Message, user_lang: str, user: dict | None):
    """
    Отображает статистику за сегодня и неделю.

    Если цель не установлена — предлагает пройти настройку.
    Иначе генерирует график и отправляет его как изображение.

    Args:
        message (Message): Входящее сообщение.
        user_lang (str): Код языка.
        user (dict | None): Данные пользователя.
    """
    user_id = message.from_user.id

    if not user or not user["daily_goal_ml"]:
        no_profile_msg = get_text("analyze.no_profile", user_lang)
        await message.answer(no_profile_msg)
        return

    goal = user["daily_goal_ml"]

    # Сегодняшние данные
    today_intakes = await get_today_intakes(user_id)
    today_total = sum(r.amount_ml for r in today_intakes)
    percent = min(100, round(today_total / goal * 100))

    # ASCII-прогресс-бар
    bar_length = 15
    filled = int(bar_length * percent / 100)
    bar_progress = "█" * filled + "░" * (bar_length - filled)

    # Еженедельные данные
    weekly_data = await get_weekly_totals(user_id)
    week_str = _format_weekly_stats(weekly_data, goal, user_lang)

    stats_text = get_text(
        "analyze.report",
        user_lang,
        current=today_total,
        goal=goal,
        percent=percent,
        bar=bar_progress,
        week_summary=week_str
    )

    # await message.answer(stats_text)

    # Генерируем график
    chart_path = generate_weekly_chart(weekly_data, goal, user_lang)
    photo = FSInputFile(chart_path)
    await message.answer_photo(photo, caption=stats_text)

    # Удаляем временный файл
    try:
        os.remove(chart_path)
    except OSError:
        pass  # Игнорируем ошибки удаления


def _format_weekly_stats(weekly_data: dict, goal: int, user_lang: str) -> str:
    """Форматирует статистику за последние 7 дней"""
    days = []
    now = datetime.now(timezone.utc).date()
    units = get_text("units.ml", user_lang)

    # Список дней: сегодня, вчера, позавчера...
    for i in range(7):
        day = now - timedelta(days=i)
        key = day.isoformat()
        amount = weekly_data.get(key, 0)
        weekday_index = day.weekday()
        if i == 0:
            label = get_text("analyze.today", user_lang)
        elif i == 1:
            label = get_text("analyze.yesterday", user_lang)
        else:
            label = f"{get_loc_list('weekday', user_lang)[weekday_index]}"  # Mon, Tue...
        if amount > 0:
            pct = min(100, round(amount / goal * 100))
            emoji = "✅" if pct >= 100 else "💧"
            days.append(f"{emoji} {label}: {amount} {units} ({pct}%)")
        else:
            days.append(f"❌ {label}: 0 {units}")

    return "\n".join(reversed(days))  # от старых к новым
