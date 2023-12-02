from src.add_numbers import add_numbers


def test_add_numbers():
    assert add_numbers(2, 2) == 4
    assert add_numbers(1, 0.36) == 1.36
    assert add_numbers(-2, 2) == 0
    assert add_numbers(1, 0.39999) == 1.39999
