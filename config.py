"""
Модуль конфигурации приложения.

Содержит настройки, загружаемые из переменных окружения (.env),
и обеспечивает валидацию с помощью Pydantic.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс настроек приложения.

    Атрибуты:
        bot_token (str): Токен Telegram-бота, полученный от @BotFather.
        db_path (str): Путь к файлу SQLite базы данных. По умолчанию — 'data/aquatrack.db'.

    Примечание:
        Загружает значения из файла .env в корне проекта.
    """

    bot_token: str
    db_path: str = "data/aquatrack.db"
    i18n_auto_generate: int = 0

    class Config:
        """Указывает Pydantic использовать файл .env для загрузки переменных."""
        env_file = ".env"
