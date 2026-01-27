# database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from .models import metadata
import os

# Путь к базе данных (по умолчанию — data/aquatrack.db)
DB_PATH = os.getenv("DB_PATH", "data/aquatrack.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Создаём асинхронный движок
# Для SQLite в памяти или файле
engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # важно для SQLite в одном файле
    echo=False,  # установите True для отладки SQL
)

# Создаём фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def init_db():
    """Создаёт таблицы при первом запуске."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)