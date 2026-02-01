"""
Модуль обработчиков (хэндлеров) событий Telegram.

Содержит роутеры для всех пользовательских сценариев:
настройка профиля, добавление воды, просмотр статистики,
управление напоминаниями, локализацией и целями.

Каждый хэндлер использует middleware для автоматического
определения языка и данных пользователя.
"""
from .start import router as start_router
from .lang import router as lang_router
from .drink import router as drink_router
from .analyze import router as analize_router
# from .settings import router as settings_router
from .reminder import router as reminder_router
from .goal import router as goal_router
