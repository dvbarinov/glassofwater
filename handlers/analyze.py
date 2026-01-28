from aiogram import Router, F
from aiogram.types import Message
from datetime import timedelta
from utils.i18n import get_text, get_user_language
from database.queries import get_user, get_today_intakes, get_weekly_totals

router = Router()


@router.message(F.text == "/analyze")
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    user_lang = await get_user_language(
        user_id,
        telegram_lang=message.from_user.language_code
    )

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
    bar = "█" * filled + "░" * (bar_length - filled)

    # Еженедельные данные
    weekly_data = await get_weekly_totals(user_id)
    week_str = _format_weekly_stats(weekly_data, goal, user_lang)

    stats_text = get_text(
        "analyze.report",
        user_lang,
        current=today_total,
        goal=goal,
        percent=percent,
        bar=bar,
        week_summary=week_str
    )

    await message.answer(stats_text)

# В том же файле analyze.py (внизу)
def _format_weekly_stats(weekly_data: dict, goal: int, lang: str) -> str:
    """Форматирует статистику за последние 7 дней"""
    from datetime import datetime, timezone
    days = []
    now = datetime.now(timezone.utc).date()

    # Список дней: сегодня, вчера, позавчера...
    for i in range(7):
        day = now - timedelta(days=i)
        key = day.isoformat()
        amount = weekly_data.get(key, 0)
        if amount > 0:
            pct = min(100, round(amount / goal * 100))
            emoji = "✅" if pct >= 100 else "💧"
            if i == 0:
                label = get_text("analyze.today", lang)
            elif i == 1:
                label = get_text("analyze.yesterday", lang)
            else:
                label = day.strftime("%a")  # Mon, Tue...
            days.append(f"{emoji} {label}: {amount} мл ({pct}%)")
        else:
            if i == 0:
                label = get_text("analyze.today", lang)
            elif i == 1:
                label = get_text("analyze.yesterday", lang)
            else:
                label = day.strftime("%a")
            days.append(f"❌ {label}: 0 мл")

    return "\n".join(reversed(days))  # от старых к новым
