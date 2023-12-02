

def add_numbers(num1: int | float, num2: int | float) -> int | float:
    float_num1_length = 0
    float_num2_length = 0
    if isinstance(num1, float):
        float_num1_length = len(str(num1).split('.')[-1])
    if isinstance(num2, float):
        float_num2_length = len(str(num2).split('.')[-1])
    return num1 + num2
