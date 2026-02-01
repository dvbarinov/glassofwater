import pytest
from database.queries import get_user, create_or_update_user, set_user_goal, toggle_notifications


@pytest.mark.asyncio
async def test_create_user():
    """Тест создания пользователя"""
    user_id = 12345

    # Создаём пользователя
    await create_or_update_user(
        user_id=user_id,
        gender=0,
        weight_kg=70,
        activity_level=1,
        daily_goal_ml=2400
    )

    # Читаем из БД
    user = await get_user(user_id)
    assert user is not None
    assert user["user_id"] == user_id
    assert user["daily_goal_ml"] == 2400
    assert user["gender"] == 0


@pytest.mark.asyncio
async def test_update_user():
    """Тест обновления пользователя"""
    user_id = 12345
    await create_or_update_user(user_id, gender=0, weight_kg=70, activity_level=1, daily_goal_ml=2400)

    # Обновляем цель
    await set_user_goal(user_id, 3000)
    user = await get_user(user_id)
    assert user["daily_goal_ml"] == 3000


@pytest.mark.asyncio
async def test_toggle_notifications():
    """Тест переключения напоминаний"""
    user_id = 12345
    await create_or_update_user(user_id, gender=0, weight_kg=70, activity_level=1, daily_goal_ml=2400)

    # Выключаем
    await toggle_notifications(user_id, False)
    user = await get_user(user_id)
    assert user["notifications_enabled"] is False

    # Включаем
    await toggle_notifications(user_id, True)
    user = await get_user(user_id)
    assert user["notifications_enabled"] is True