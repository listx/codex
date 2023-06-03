from hypothesis import given, strategies as st
import unittest

def even_odd(ints):
  idx_even = 0
  idx_odd = len(ints) - 1

  while idx_even < idx_odd:
    if ints[idx_odd] & 1:
      idx_odd -= 1
    else:
      ints[idx_even], ints[idx_odd] = ints[idx_odd], ints[idx_even]
      idx_even += 1

  # Return the number of even numbers found.
  if ints and ints[idx_even] & 1 == 0:
    idx_even += 1
  return idx_even

class Test(unittest.TestCase):
  cases = [
    ([],        [],        0),
    ([0],       [0],       1),
    ([1],       [1],       0),
    ([0, 2],    [2, 0],    2),
    ([1, 2],    [2, 1],    1),
    ([0, 2, 3], [2, 0, 3], 2),
    ([0, 3, 2], [2, 0, 3], 2),
    ([1, 3, 5], [1, 3, 5], 0),
    ([2, 4, 6], [6, 2, 4], 3),
  ]

  def test_simple_cases(self):
    for given_ints, expected_ints, expected_evens in self.cases:
      got_evens = even_odd(given_ints)

      self.assertEqual(given_ints, expected_ints)
      self.assertEqual(got_evens, expected_evens)

  @given(st.lists(st.integers(min_value=0, max_value=100), min_size=0,
                  max_size=16))
  def test_random(self, given_ints):
    even_nums = even_odd(given_ints)
    # If we found some even numbers, these elements must actually all be even.
    # And the remaining elements (if any) must all be odd.
    if even_nums > 0:
      for i in range(0, even_nums):
        self.assertFalse(given_ints[i] & 1)
      for j in range(even_nums, len(given_ints)):
        self.assertTrue(given_ints[j] & 1)
    # If we did not find any even numbers, but the given list was not empty,
    # then it means that all numbers in the list are odd.
    elif given_ints:
      for j in range(0, len(given_ints)):
        self.assertTrue(given_ints[j] & 1)

if __name__ == "__main__":
  unittest.main(exit=False)
