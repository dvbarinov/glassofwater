import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from handlers.reminders import send_reminder

async def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    # Пример: напоминать каждые 2 часа с 9:00 до 21:00
    for hour in range(9, 22, 2):
        trigger = CronTrigger(hour=hour, minute=0, timezone="UTC")
        scheduler.add_job(send_reminder, trigger, args=[bot])
    scheduler.start()