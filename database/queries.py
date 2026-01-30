"""
Модуль выполнения запросов к базе данных.

Содержит функции для CRUD-операций с пользователями и записями о воде.
Все функции асинхронны и используют AsyncSessionLocal из engine.py.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, insert, update, func
from .models import users, intakes
from .engine import AsyncSessionLocal

async def get_user(user_id: int):
    """
    Получает данные пользователя по его Telegram ID.

    Args:
        user_id (int): Уникальный идентификатор пользователя в Telegram.

    Returns:
        sqlalchemy.engine.Row | None: Строка из таблицы users или None, если не найден.
    """
    async with AsyncSessionLocal() as session:
        query = select(users).where(users.c.user_id == user_id)
        result = await session.execute(query)
        row = result.mappings().fetchone()
        return dict(row) if row else None

async def create_or_update_user(user_id: int, **kwargs):
    """
    Создаёт нового пользователя или обновляет существующего.

    Args:
        user_id (int): Telegram ID пользователя.
        **kwargs: Поля для сохранения (gender, weight_kg, daily_goal_ml и т.д.).
    """
    async with AsyncSessionLocal() as session:
        existing = await get_user(user_id)
        if existing:
            stmt = update(users).where(users.c.user_id == user_id).values(**kwargs)
        else:
            kwargs["user_id"] = user_id
            stmt = insert(users).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

async def set_user_language(user_id: int, lang: str):
    async with AsyncSessionLocal() as session:
        # Убедимся, что пользователь существует
        existing = await get_user(user_id)
        if not existing:
            # Создаём "заглушку", если пользователь не прошёл настройку
            stmt = insert(users).values(user_id=user_id, language=lang)
        else:
            stmt = update(users).where(users.c.user_id == user_id).values(language=lang)
        await session.execute(stmt)
        await session.commit()

async def add_intake(user_id: int, amount_ml: int):
    """
    Добавляет запись о потреблении воды.

    Args:
        user_id (int): Telegram ID пользователя.
        amount_ml (int): Количество выпитой воды в миллилитрах.
    """
    async with AsyncSessionLocal() as session:
        stmt = insert(intakes).values(
            user_id=user_id,
            amount_ml=amount_ml,
            timestamp=datetime.now(timezone.utc)
        )
        await session.execute(stmt)
        await session.commit()

async def get_today_intakes(user_id: int):
    """
    Возвращает все записи о воде за сегодняшний день (UTC).

    Args:
        user_id (int): Telegram ID пользователя.

    Returns:
        list[sqlalchemy.engine.Row]: Список записей.
    """
    today = datetime.now(timezone.utc).date()
    async with AsyncSessionLocal() as session:
        query = (
            select(intakes)
            .where(intakes.c.user_id == user_id)
            .where(func.date(intakes.c.timestamp) == today)
            .order_by(intakes.c.timestamp)
        )
        result = await session.execute(query)
        return result.fetchall()


async def get_weekly_totals(user_id: int):
    """
    Возвращает суммарное потребление воды за последние 7 дней.

    Args:
        user_id (int): Telegram ID пользователя.

    Returns:
        dict[str, int]: Словарь вида {"YYYY-MM-DD": total_ml}.
    """
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    async with AsyncSessionLocal() as session:
        query = (
            select(
                func.date(intakes.c.timestamp).label("date"),
                func.sum(intakes.c.amount_ml).label("total")
            )
            .where(intakes.c.user_id == user_id)
            .where(intakes.c.timestamp >= week_ago)
            .group_by(func.date(intakes.c.timestamp))
        )
        result = await session.execute(query)
        rows = result.fetchall()
        return {str(row.date): row.total for row in rows}

async def toggle_notifications(user_id: int, enabled: bool):
    """Переключает статус напоминаний для пользователя."""
    await create_or_update_user(user_id, notifications_enabled=enabled)

async def get_all_active_users():
    """Возвращает всех пользователей с включёнными напоминаниями"""
    async with AsyncSessionLocal() as session:
        query = select(users).where(users.c.notifications_enabled == True)
        result = await session.execute(query)
        return result.mappings().fetchall()

async def set_user_goal(user_id: int, goal_ml: int):
    """Устанавливает суточную цель пользователя"""
    await create_or_update_user(user_id, daily_goal_ml=goal_ml)
