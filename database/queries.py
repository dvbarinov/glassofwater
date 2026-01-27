# database/queries.py
from sqlalchemy import select, insert, update
from .models import users
from .engine import AsyncSessionLocal

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        query = select(users).where(users.c.user_id == user_id)
        result = await session.execute(query)
        return result.fetchone()._asdict() if result.fetchone() else None

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