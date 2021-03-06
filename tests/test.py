import mpmath
import pytest
from mpmath import mp

from cafe18.cafe5 import cafeize, decrypt, encrypt, integer_part_log, integer_part_power


@pytest.mark.parametrize(
    ["input_str", "expected_str"],
    [
        ("f4 / f", "e"),
        ("f4 / e", "f"),
        ("f4 / c", "f4"),
        ("f3 * e", "f7"),
        ("e8 / c", "e8"),
        ("e - c", "c"),
        ("e - 8", "e"),
        ("f3 + c", "f4"),
        ("f7 + e", "f8"),
        ("e8 * f", "f6"),
        ("8 / e8", "8"),
        ("f18 + 8", "f18"),
        ("8 + f7", "f7"),
        ("f4 + f2", "f7"),
        ("f5 + f2", "f8"),
        ("e * 8", "8"),
        ("e8 * 8", "8"),
        ("f68 * c", "f68"),
        ("f + f2", "f5"),
        ("e / e", "c"),
        ("F8 / F4", "E"),
        ("8 + F58", "F58"),
        ("F3 - F18", "E"),
        ("c * F18", "f18"),
        ("e + c", "e8"),
        ("f74 - E", "f68"),
        ("F8a / F7", "E"),
        ("F18 - F", "C"),
        ("F6 - F", "F4"),
        ("F48 / E8", "E8"),
        ("e8 + E8", "f2"),
        ("f - c", "e8"),
        ("C + 18", "2"),
        ("071D / 0B", "F18"),
        ("2 * 4", "E"),
        ("0738 / f48", "1"),
        ("0E8 - 1", "4"),
        ("4 - 0D", "F2"),
        ("F738 + 2", "f67"),
        ("0A8 - E8", "09"),
        ("F99E4 / 0A", "0958"),
        ("06F0E8 / F38", "0b8"),
        ("FC735C7388D89271CBC4 / FC5294DAB8D", "fc4878736b8c"),
        ("FC71875CACE31C7A876 / FC39768768", "fc599d58d98c"),
        ("FC638C mod F56", "f0e8"),
        ("FCC39D mod F5", "e"),
    ],
)
def test_cafe18(input_str, expected_str):
    assert cafeize(input_str) == expected_str.lower()


@pytest.mark.parametrize(
    ["input_str", "unexpected_str"],
    [
        ("FC638C mod F56", "f0e78f14"),
        ("1071D * F3072E", "076"),
        ("F1831C - 0B416298", "f72"),
        ("FC6BC mod E9", "e473"),
        ("FCC39D mod F5", "f2"),
        ("FE13DC05 mod F28", "OverflowError")
    ],
)
def test_wrong_results(input_str, unexpected_str):
    assert cafeize(input_str) != unexpected_str.lower()


@pytest.mark.parametrize(
    ["input_str", "expected_result"],
    [
        ("8", 0),  # 1000 - 0000  / 1 0000
        ("c", 1),  # 1100 - 0001  / 1 1000
        ("e", 2),  # 1110 - 0010  / 1 1100
        ("e8", 3),  # 1110 1000 - 0011 / 1 1101
        ("f", 4),  # 1111 - 0100 /    1 1110
        ("f18", 5),  # 1111 0001 1000 - 0101 / 1 1110 0011
        ("f2", 6),  # 1111 0010 - 0110 / 1 1110 0100
        ("f3", 7),  # 1111 0011 - 0111 / 1 1110 0110
        ("f4", 8),  # 1111 0100 - 1000 / 1 1110 1000
        ("f48", 9),  # 1111 0100 1000 - 1001 / 1 1110 1001
        ("f5", 10),  # 1111 0101 - 1010 / 1 1110 1010
        ("f58", 11),  # 1111 0101 1000 - 1011 / 1 1110 1011
        ("f6", 12),  # 1111 0110 - 1100 / 1 1110 1100
        ("f68", 13),  # 1111 0110 1000 - 1101 / 1 1110 1101
        ("f7", 14),  # 1111 0111 - 1110 / 1 1110 1110
        ("f74", 15),  # 1111 0111 0100 - 1111 / 1 1110 1110 1000
        ("f8", 16),  # 1111 1000 - 0001 0000 / 1 1111
        ("f87", 18),  # 1111 1000 0111 - 0001 0010
        ("f872", 19),  # 1111 1000 0111 0010 - 0001 0011
        ("f874", 20),  # 1111 1000 0111 0100 - 0001 0100
        ("f876", 21),  # 1111 1000 0111 0110 - 0001 0101
        ("f878", 22),  # 1111 1000 0111 1000 - 0001 0110
        ("f88", 24),  # 1111 1000 1000 - 0001 1000
        ("f8a", 28),  # 1111 1000 1010 - 0001 1100
        ("f8a8", 29),  # 1111 1000 1010 1000 - 0001 1101
        ("f8b", 30),  # 1111 1000 1011 - 0001 1110
        ("f8c", 32),  # 1111 1000 1100
        ("f8d", 40),
        ("f8e", 48),
        ("f9", 64),  # 1111 1001
        ("f918", 72),
        ("f952", 105),
        ("f99a", 154),  # 1111 1001 1001 1010
        ("4", -1),  # 0100
        ("2", -2),  # 0010
        ("18", -3),  # 0001 1000
        ("1", -4),  # 0001
        ("0e8", -5),  # 0000 1110 1000
        # ("0e", -6),  # 0000 1110
        ("0d", -7),  # 0000 1100
        ("0738", -36),
    ],
)
def test_decrypt(input_str, expected_result):
    result = decrypt(input_str)
    assert mpmath.nstr(result) == mpmath.nstr(mp.mpf(expected_result))


@pytest.mark.parametrize(
    ["input_int", "expected_result"],
    [
        (0, "8"),  # 1000
        (1, "c"),  # 1100
        (2, "e"),  # 1110
        (3, "e8"),  # 1110 1000
        (4, "f"),  # 1111
        (5, "f18"),  # 1111 0001 1000
        (6, "f2"),  # 1111 0010
        (7, "f3"),  # 1111 0011
        (8, "f4"),  # 1111 0100
        (9, "f48"),  # 1111 0100 1000
        (10, "f5"),  # 1111 0101
        (11, "f58"),  # 1111 0101 1000
        (12, "f6"),  # 1111 0110
        (13, "f68"),  # 1111 0110 1000
        (14, "f7"),  # 1111 0111
        (15, "f74"),  # 1111 0111 0100
        (16, "f8"),  # 1111 1000
        (28, "f8a"),
        (30, "f8b"),
        (-1, "4"),  # 0100
        (-2, "2"),  # 0010
        (-3, "18"),  # 0001 1000
        (-4, "1"),  # 0001
        (-5, "0e8"),  # 0000 1110 1000
        (-7, "0d"),  # 0000 1100
        (-36, "0738"),
        (72, "f918"),
        (105, "f952"),
        (154, "f99a"),
    ],
)
def test_encrypt(input_int, expected_result):
    assert encrypt(input_int) == expected_result


@pytest.mark.parametrize(
    "input_str",
    [
        "f",
        "c",
        "8",
        "f5",
        "e8",
        "f95",
        "f8f",
        "f8e2",
        "f90e8",
        "f99c",
        "f9a8",
        "f878",
        "F91D",
        "F8CE",
    ],
)
def test_parse_valid_operand(input_str):
    assert decrypt(input_str) is not None


@pytest.mark.parametrize(
    "input_number",
    [0, 0.5, 1, 2, 3, 3.5, 4, 5.25, 5, -1, -0.5, -2, -3.5, -1.125, 100, -1010],
)
def test_integer_part_log_reverse(input_number):
    assert integer_part_log(integer_part_power(input_number)) == input_number
