from datetime import datetime, timezone, timedelta
from sqlalchemy import select, insert, update, func
from .models import users, intakes
from .engine import AsyncSessionLocal

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        query = select(users).where(users.c.user_id == user_id)
        result = await session.execute(query)
        row = result.mappings().fetchone()
        return dict(row) if row else None

async def create_or_update_user(user_id: int, gender: int, weight_kg: int, activity_level: int, daily_goal_ml: int):
    async with AsyncSessionLocal() as session:
        existing = await get_user(user_id)
        if existing:
            stmt = (
                update(users)
                .where(users.c.user_id == user_id)
                .values(
                    gender=gender,
                    weight_kg=weight_kg,
                    activity_level=activity_level,
                    daily_goal_ml=daily_goal_ml
                )
            )
        else:
            stmt = insert(users).values(
                user_id=user_id,
                gender=gender,
                weight_kg=weight_kg,
                activity_level=activity_level,
                daily_goal_ml=daily_goal_ml
            )
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
    """Добавляет запись о выпитой воде"""
    async with AsyncSessionLocal() as session:
        stmt = insert(intakes).values(
            user_id=user_id,
            amount_ml=amount_ml,
            timestamp=datetime.now(timezone.utc)
        )
        await session.execute(stmt)
        await session.commit()

async def get_today_intakes(user_id: int):
    """Возвращает все записи за сегодня"""
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
    """Возвращает словарь: {дата_iso: сумма_мл} за последние 7 дней"""
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
    async with AsyncSessionLocal() as session:
        stmt = (
            update(users)
            .where(users.c.user_id == user_id)
            .values(notifications_enabled=enabled)
        )
        await session.execute(stmt)
        await session.commit()

async def get_all_active_users():
    """Возвращает всех пользователей с включёнными напоминаниями"""
    async with AsyncSessionLocal() as session:
        query = select(users).where(users.c.notifications_enabled == True)
        result = await session.execute(query)
        return result.mappings().fetchall()
