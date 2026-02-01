# tests/test_handlers.py
import unittest

def is_valid_water_amount(amount: str) -> bool:
    """Вспомогательная функция из drink.py (вынесена для тестирования)"""
    try:
        val = int(amount)
        return 50 <= val <= 3000
    except ValueError:
        return False

class TestInputValidation(unittest.TestCase):

    def test_valid_amounts(self):
        self.assertTrue(is_valid_water_amount("100"))
        self.assertTrue(is_valid_water_amount("2500"))
        self.assertTrue(is_valid_water_amount("50"))
        self.assertTrue(is_valid_water_amount("3000"))

    def test_invalid_amounts(self):
        self.assertFalse(is_valid_water_amount("49"))
        self.assertFalse(is_valid_water_amount("3001"))
        self.assertFalse(is_valid_water_amount("abc"))
        self.assertFalse(is_valid_water_amount(""))

if __name__ == '__main__':
    unittest.main()