# tests/test_validation.py
import pytest

@pytest.mark.parametrize("amount,expected", [
    ("100", True),
    ("2500", True),
    ("50", True),
    ("3000", True),
    ("49", False),
    ("3001", False),
    ("abc", False),
    ("", False),
    ("-100", False),
])
def test_water_amount_validation(amount, expected):
    """Проверка валидности объёма воды"""
    try:
        val = int(amount)
        is_valid = 50 <= val <= 3000
    except ValueError:
        is_valid = False
    assert is_valid == expected