"""
Точка входа Telegram-бота AquaTrack.

Инициализирует компоненты приложения:
- подключение к базе данных,
- маршрутизацию сообщений,
- планировщик напоминаний,
- логирование.

Запускает бота в режиме polling.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from middlewares.i18n import I18nMiddleware
from config import Settings
from database.engine import init_db, AsyncSessionLocal
from handlers import (
    start_router,
    lang_router,
    drink_router,
    analize_router,
    # settings_router,
    reminder_router,
    goal_router,
)
from services.scheduler import setup_scheduler
from utils.i18n import load_locales

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная асинхронная функция запуска бота.

    Выполняет следующие шаги:
        1. Загружает конфигурацию из .env.
        2. Инициализирует базу данных (создаёт таблицы при первом запуске).
        3. Настраивает бота и диспетчер.
        4. Подключает middleware для локализации.
        5. Регистрирует все маршруты (хэндлеры).
        6. Запускает polling-режим для получения обновлений от Telegram.

    Исключения:
        KeyboardInterrupt, SystemExit: корректно завершает работу при остановке.
    """

    # Загрузка конфигурации
    settings = Settings()
    load_locales()

    # Инициализация БД
    await init_db()
    logger.info("✅ База данных инициализирована")

    # Инициализация бота и диспетчера
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Применяем мидлварь ко всем сообщениям и колбэкам
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Подключение маршрутов (роутеров)
    dp.include_router(start_router)
    dp.include_router(lang_router)
    dp.include_router(drink_router)
    dp.include_router(analize_router)
    # dp.include_router(settings_router)
    dp.include_router(reminder_router)
    dp.include_router(goal_router)

    # Настройка планировщика напоминаний
    await setup_scheduler(bot)

    # Запуск polling
    logger.info("🚀 Запуск бота...")
    await dp.start_polling(bot, session_factory=AsyncSessionLocal)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    #Обеспечивает корректную обработку прерываний (Ctrl+C) и завершение работы.
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен.")
