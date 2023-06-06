import unittest

from typing import Optional

def is_palindrome(s: str) -> bool:
  return all(s[i] == s[~i] for i in range(len(s) // 2))

class Test(unittest.TestCase):

  def test_simple_cases(self):
    pass

if __name__ == "__main__":
  unittest.main(exit=False)
