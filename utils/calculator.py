# utils/calculator.py
def calculate_daily_water_goal(gender: int, weight_kg: int, activity_level: int) -> int:
    """
    Рассчитывает суточную норму воды в мл.
    gender: 0 = male, 1 = female
    activity_level: 0 = low, 1 = medium, 2 = high
    """
    base = weight_kg * 30  # 30 мл на кг
    activity_bonus = {0: 0, 1: 300, 2: 600}[activity_level]

    # Женщинам немного меньше (по некоторым рекомендациям)
    if gender == 1:
        base = int(base * 0.9)

    total = base + activity_bonus
    return max(1200, min(5000, total))  # Ограничение разумных рамок