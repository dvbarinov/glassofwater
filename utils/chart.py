import os
import matplotlib

from utils.i18n import get_loc_list, get_text

matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from typing import Dict


def generate_weekly_chart(
        weekly_data: Dict[str, int],
        goal_ml: int,
        lang: str = "en"
) -> str:
    """
    Генерирует график за последние 7 дней и сохраняет в файл.
    Возвращает путь к файлу.
    """
    # Настройка локали для подписей
    labels = get_loc_list("weekday", lang)
    units = get_text("ml", lang)
    goal = get_text("analyze.goal", lang)

    # Подготовка данных
    today = datetime.now(timezone.utc).date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]  # от старых к новым
    amounts = [weekly_data.get(date.isoformat(), 0) for date in dates]
    days = [labels[date.weekday()] for date in dates]

    # Создание графика
    plt.figure(figsize=(8, 4))
    bars = plt.bar(days, amounts, color='#4CAF50', edgecolor='black', linewidth=0.5)

    # Линия цели
    plt.axhline(y=goal_ml, color='#FF5722', linestyle='--', linewidth=2, label=f'{goal}: {goal_ml} {units}')

    # Подписи на столбцах
    for bar, amount in zip(bars, amounts):
        if amount > 0:
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(amount * 0.02, 20),
                f'{amount}',
                ha='center', va='bottom', fontsize=9, fontweight='bold'
            )

    plt.ylim(0, max(goal_ml * 1.3, max(amounts or [1]) * 1.3))
    plt.ylabel(units, fontsize=10)
    plt.title(get_text("analyze.chart", lang), fontsize=12)
    plt.legend()
    plt.tight_layout()

    # Сохранение
    os.makedirs("temp", exist_ok=True)
    filename = f"temp/chart_{hash(str(weekly_data)) % 1000000}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()  # Освобождаем память

    return filename
