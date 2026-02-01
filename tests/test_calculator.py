import unittest
from utils.calculator import calculate_daily_water_goal

class TestWaterGoalCalculation(unittest.TestCase):

    def test_male_average(self):
        # Мужчина, 70 кг, средняя активность
        goal = calculate_daily_water_goal(gender=0, weight_kg=70, activity_level=1)
        self.assertEqual(goal, 70*35+300)  # 70*30 + 300 = 2400

    def test_female_average(self):
        # Женщина, 60 кг, низкая активность
        goal = calculate_daily_water_goal(gender=1, weight_kg=60, activity_level=0)
        expected = int(60 * 35 * 0.9)  # 1620 → но не менее 1200
        self.assertEqual(goal, max(1200, expected))

    def test_high_activity(self):
        goal = calculate_daily_water_goal(gender=0, weight_kg=80, activity_level=2)
        self.assertEqual(goal, 80*35 + 600)  # 3000

    def test_bounds(self):
        # Очень лёгкий человек
        goal = calculate_daily_water_goal(gender=0, weight_kg=30, activity_level=0)
        self.assertGreaterEqual(goal, 1200)

        # Очень тяжёлый
        goal = calculate_daily_water_goal(gender=0, weight_kg=200, activity_level=2)
        self.assertLessEqual(goal, 5000)

if __name__ == '__main__':
    unittest.main()