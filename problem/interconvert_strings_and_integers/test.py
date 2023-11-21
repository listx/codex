from hypothesis import given, strategies as st
import unittest

import functools

def int_to_str(n: int) -> str:
    negative = False
    if n < 0:
        negative = True
        n = -n
    digits = []
    while True:
        digit = n % 10
        digit_ascii_codepoint = ord('0') + digit
        digits.append(chr(digit_ascii_codepoint))
        n //= 10
        if n == 0:
            break
    res = "-" if negative else ""
    res += "".join(reversed(digits))
    return res
def str_to_int(s: str) -> int:
    res = 0

    if not s:
        return res
    negative = False
    if s[0] == "-":
        negative = True
        s = s[1:] # Drop the "-" character.
    for power, digit in enumerate(reversed(s)):
        num = ord(digit) - ord("0")
        res += (10**power) * num

    if negative:
        res *= -1

    return res
def str_to_int_functional(s: str) -> int:
    res = functools.reduce(
        lambda partial_sum, digit: partial_sum * 10 + (ord(digit) - ord('0')),
        s[s[0] == "-":],
        0)
    if s[0] == "-":
        res *= -1
    return res

class Test(unittest.TestCase):
    cases = [
        (-234,  "-234"),
        (-1,  "-1"),
        (0,   "0"),
        (1,   "1"),
        (123, "123"),
    ]

    def test_simple_cases(self):
        for given_int, expected in self.cases:
            self.assertEqual(int_to_str(given_int), expected,
                             msg=f'{given_int=}')

        for expected, given_str in self.cases:
            self.assertEqual(str_to_int(given_str), expected,
                             msg=f'{given_str=}')

    @given(st.integers(min_value=-1000000, max_value=1000000))
    def test_random(self, given_int: int):
        got_str = int_to_str(given_int)
        got_int = str_to_int(got_str)
        got_int_functional = str_to_int_functional(got_str)
        # Check roundtrip.
        self.assertEqual(got_int, given_int, msg=f'{given_int=}')
        self.assertEqual(got_int_functional, given_int, msg=f'{given_int=}')

if __name__ == "__main__":
    unittest.main(exit=False)
