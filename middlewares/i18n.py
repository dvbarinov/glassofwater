"""
Мидлварь для автоматического определения языка интерфейса.

Извлекает данные пользователя из базы данных, определяет финальный язык
с учётом приоритетов (БД → Telegram → fallback) и внедряет его в контекст
обработки сообщения или callback-запроса.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from database.queries import get_user
from utils.i18n import get_user_language


class I18nMiddleware(BaseMiddleware):
    """
    Middleware для подготовки локализационного контекста.

    Добавляет в data следующие ключи:
        - 'lang' (str): код выбранного языка (например, 'ru', 'en')
        - 'user' (dict | None): данные пользователя из БД или None

    Приоритет выбора языка:
        1. Язык, сохранённый пользователем в профиле (поле 'language' в БД)
        2. Язык интерфейса Telegram (message.from_user.language_code)
        3. Английский ('en') как fallback

    Примечание:
        Работает как с Message, так и с CallbackQuery.
    """

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        """
        Выполняет middleware-логику перед вызовом хэндлера.

        Args:
            handler: Следующий обработчик в цепочке (обычно хэндлер).
            event: Входящее событие (сообщение или callback).
            data: Контекстные данные, передаваемые между middleware и хэндлером.

        Returns:
            Результат выполнения следующего обработчика.
        """
        user_id = event.from_user.id
        telegram_lang = event.from_user.language_code or "ru"
        user = await get_user(user_id)

        # Определяем финальный язык
        lang = await get_user_language(user, user_id, telegram_lang)

        # Передаём язык в контекст хэндлера
        data["lang"] = lang
        data["user_lang"] = lang
        data["user"] = user  # на случай, если понадобится

        return await handler(event, data)
