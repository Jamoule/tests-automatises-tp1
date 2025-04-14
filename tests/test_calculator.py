import pytest
from app.calculator import Calculator

def test_add():
    calculator = Calculator()
    assert calculator.add(1, 2) == 3
    assert calculator.add(-1, 1) == 0
    assert calculator.add(-1, -1) == -2
    assert calculator.add(0, 0) == 0
    assert calculator.add(100, 200) == 300

def test_subtract():
    calculator = Calculator()
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(3, 5) == -2
    assert calculator.subtract(-1, -1) == 0
    assert calculator.subtract(0, 0) == 0
    assert calculator.subtract(10, 0) == 10
    assert calculator.subtract(0, 10) == -10

def test_multiply():
    calculator = Calculator()
    assert calculator.multiply(2, 3) == 6
    assert calculator.multiply(-2, 3) == -6
    assert calculator.multiply(2, -3) == -6
    assert calculator.multiply(-2, -3) == 6
    assert calculator.multiply(0, 5) == 0
    assert calculator.multiply(5, 0) == 0

def test_divide():
    calculator = Calculator()
    assert calculator.divide(6, 3) == 2
    assert calculator.divide(-6, 3) == -2
    assert calculator.divide(6, -3) == -2
    assert calculator.divide(-6, -3) == 2
    assert calculator.divide(0, 5) == 0
    assert calculator.divide(7, 2) == 3.5

def test_divide_by_zero():
    calculator = Calculator()
    with pytest.raises(ZeroDivisionError):
        calculator.divide(6, 0)
    with pytest.raises(ZeroDivisionError):
        calculator.divide(0, 0)
    with pytest.raises(ZeroDivisionError):
        calculator.divide(-5, 0)
