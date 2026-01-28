from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time, timezone, timedelta
import pytz

from database.queries import get_all_active_users
from utils.i18n import get_text, get_user_language

# Глобальный бот (будет установлен в main.py)
_bot = None

def set_bot(bot):
    global _bot
    _bot = bot

async def send_water_reminder():
    """Отправляет напоминание всем активным пользователям"""
    if _bot is None:
        return

    users = await get_all_active_users()
    now_utc = datetime.now(timezone.utc)

    for user in users:
        try:
            # Определяем локальное время пользователя
            tz_offset = user["timezone_offset"]  # в минутах от UTC
            user_tz = pytz.FixedOffset(tz_offset)
            local_time = now_utc.astimezone(user_tz).time()

            # Отправляем напоминание только в рабочие часы (9:00–21:00)
            if time(9, 0) <= local_time <= time(21, 0):
                lang = user["language"] or "ru"
                msg = get_text("reminders.notification", lang)

                # Добавляем быстрые кнопки
                from keyboards.inline import get_drink_quick_buttons
                await _bot.send_message(
                    chat_id=user["user_id"],
                    text=msg,
                    reply_markup=get_drink_quick_buttons(lang)
                )
        except Exception as e:
            print(f"Failed to send reminder: {e}")

async def setup_scheduler(bot):
    """Запускает планировщик напоминаний"""
    set_bot(bot)
    scheduler = AsyncIOScheduler()
    # Напоминание каждые 2 часа
    scheduler.add_job(send_water_reminder, 'interval', hours=2, next_run_time=datetime.now() + timedelta(seconds=10))
    scheduler.start()
    print("✅ Scheduler started")