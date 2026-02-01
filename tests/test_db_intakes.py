import pytest
from datetime import datetime, timezone
from database.queries import add_intake, get_today_intakes, get_weekly_totals


@pytest.mark.asyncio
async def test_add_intake():
    """Тест добавления записи о воде"""
    user_id = 12345
    amount = 250

    await add_intake(user_id, amount)

    records = await get_today_intakes(user_id)
    assert len(records) == 1
    assert records[0].amount_ml == amount


@pytest.mark.asyncio
async def test_get_weekly_totals():
    """Тест агрегации за неделю"""
    user_id = 12345

    # Добавляем записи за сегодня
    await add_intake(user_id, 200)
    await add_intake(user_id, 300)

    weekly = await get_weekly_totals(user_id)
    today = datetime.now(timezone.utc).date().isoformat()

    assert today in weekly
    assert weekly[today] == 500
