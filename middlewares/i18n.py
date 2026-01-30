from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from database.queries import get_user
from utils.i18n import get_user_language


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
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
