import math

import mpmath
from mpmath import mp

mp.dps = 3080
mp.pretty = True


def number(n):
    return mp.mpf(n)


def floor(n):
    return mp.floor(n)


def log2(n):
    return mpmath.log(n, 2)


def integer_part_power(k: float):
    integer_part = floor(k)
    remainder_log = k - integer_part

    two_to_the_remainder = remainder_log + number(1)

    remainder = log2(two_to_the_remainder)

    result = number(2) ** (integer_part + remainder)
    return result


def integer_part_log(n: float):
    log2n = log2(n)
    integer_part = floor(log2n)
    remainder = log2n - integer_part
    two_to_the_remainder = number(2) ** remainder
    result = integer_part + two_to_the_remainder - number(1)
    return result


def twos_comp(bin_str):
    complement_bits = []
    for i, elem in enumerate(bin_str):
        if i == len(bin_str) - 1:
            complement_bits.append(elem)
        else:
            complement_bits.append("1" if elem == "0" else "0")
    return complement_bits


def custom_round(n):
    n_str = str(n)
    repetition_to_round = 4
    before_dot, after_dot = n_str.split(".")

    round_index = after_dot.find("0" * repetition_to_round)
    if round_index >= 0:
        after_dot = after_dot[:round_index]

    round_index = after_dot.find("9" * repetition_to_round)
    if round_index >= 0:
        after_dot = after_dot[:round_index]
        if after_dot:
            last_digit = str(int(after_dot[-1]) + 1)
            after_dot = after_dot[:-1] + last_digit
        else:
            addition = number(-1) if before_dot[0] == "-" else number(1)
            return number(before_dot) + addition

    result = number(f"{before_dot}.{after_dot}")
    return result


def decrypt(o_str: str) -> float:
    bin_str = bin(int(o_str, 16))[2:].zfill(len(o_str) * 4)
    bin_str = bin_str.rstrip("0")
    sign = bin_str[0]
    bin_str = bin_str[1:]
    if sign == "0":
        bin_str = twos_comp(bin_str)
    reversed_str = list(reversed(bin_str))

    current = number(0)
    for i, letter in enumerate(reversed_str):

        current_sign = number(1)
        if i < len(reversed_str) - 1 and reversed_str[i + 1] == "0":
            current_sign = -number(1)

        current = current_sign * integer_part_power(current_sign * current)

    result = current
    result *= 1 if sign == "1" else -1
    return result


def encrypt(operand: float) -> str:
    result = ""
    epsilon = number("1e-308")
    current = number(operand)
    while True:
        if current >= -epsilon:
            next_sign = number(1)
            result += "1"
            if -epsilon < current < epsilon:
                break
        else:
            current = -current
            next_sign = number(-1)
            result += "0"

        current = next_sign * integer_part_log(current)

        if len(result) >= 40000:
            raise ValueError(f"Result too long for encrypting {operand}")

    zeros_to_add = 4 * math.ceil(len(result) / 4) - len(result)
    res = result + "0" * int(zeros_to_add)

    hex_result = ""
    for i in range(0, len(res), 4):
        hex_result += hex(int(res[i : i + 4], 2))[2:]

    return hex_result


def cafeize(input_str: str) -> str:
    input_str = input_str.strip().lower()
    a, oper, b = input_str.split(" ")

    a = decrypt(a)
    b = decrypt(b)

    result = None
    if oper == "+":
        result = a + b
    elif oper == "-":
        result = a - b
    elif oper == "/":
        result = a / b
    elif oper == "*":
        result = a * b
    elif oper == "mod":
        result = mpmath.fmod(a, b)

    print(f"{a} {oper} {b} = {result}")
    result_str = encrypt(result)
    return result_str


if __name__ == "__main__":
    print(encrypt(40))
    print(decrypt("F180A04FB0986439E7"))
