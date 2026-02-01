from utils.calculator import calculate_daily_water_goal


def test_male_average():
    """Мужчина, 70 кг, средняя активность"""
    goal = calculate_daily_water_goal(gender=0, weight_kg=70, activity_level=1)
    assert goal == 70*35 + 300


def test_female_average():
    """Женщина, 60 кг, низкая активность"""
    goal = calculate_daily_water_goal(gender=1, weight_kg=60, activity_level=0)
    expected = int(60 * 35 * 0.9)  # 1620
    assert goal == max(1200, expected)


def test_high_activity():
    """Высокая активность"""
    goal = calculate_daily_water_goal(gender=0, weight_kg=80, activity_level=2)
    assert goal == 80 * 35 + 600  # 3000


def test_bounds():
    """Проверка границ"""
    # Минимум
    goal = calculate_daily_water_goal(gender=0, weight_kg=30, activity_level=0)
    assert goal >= 1200

    # Максимум
    goal = calculate_daily_water_goal(gender=0, weight_kg=200, activity_level=2)
    assert goal <= 5000
