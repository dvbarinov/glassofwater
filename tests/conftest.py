# tests/conftest.py
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from database.models import metadata
from database.engine import AsyncSessionLocal

# Глобальный движок для тестов
_test_engine = None


# Фикстура для создания движка в памяти
@pytest.fixture(scope="session")
def event_loop():
    """Обеспечивает совместимость с pytest-asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
def setup_test_db(event_loop):
    """Настраивает временную БД перед каждым тестом"""
    global _test_engine

    # Создаём in-memory SQLite
    _test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаём таблицы
    async def init():
        async with _test_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    event_loop.run_until_complete(init())

    # Подменяем сессию
    AsyncSessionLocal.configure(bind=_test_engine)

    yield  # запуск теста

    # Очищаем
    AsyncSessionLocal.configure(bind=None)
    event_loop.run_until_complete(_test_engine.dispose())
