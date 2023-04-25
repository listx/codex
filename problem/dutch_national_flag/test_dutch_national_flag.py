from hypothesis import given, strategies as st
import unittest

def dutch_flag_partition(nums, idx_pivot):
  if not nums:
    return 0, 0

  # If the given idx_pivot is out of bounds, just use 0. This is the pivot
  # *index*, so we will use the value (whatever it is) at index 0 as the pivot.
  if idx_pivot < 0 or idx_pivot > (len(nums) - 1):
    idx_pivot = 0

  pivot = nums[idx_pivot]
  # Track numbers less than pivot.
  idx_lt = 0
  # Track numbers equal to pivot.
  idx_eq = 0
  # Track numbers greater than pivot. Note that this index is out-of-bounds.
  idx_gt = len(nums)

  while idx_eq < idx_gt:
    if nums[idx_eq] == pivot:
      idx_eq += 1
    elif nums[idx_eq] < pivot:
      nums[idx_lt], nums[idx_eq] = nums[idx_eq], nums[idx_lt]
      idx_lt += 1
      idx_eq += 1
    else:
      idx_gt -= 1
      nums[idx_eq], nums[idx_gt] = nums[idx_gt], nums[idx_eq]

  # Return (1) the count of numbers less than the pivot, and (2) the count of
  # numbers equal to the pivot.

  return idx_lt, idx_eq - idx_lt

class Test(unittest.TestCase):
  cases = [
    ([],                    0, [],                    0, 0),
    ([0],                   0, [0],                   0, 1),
    ([0, 0, 0, 0],          0, [0, 0, 0, 0],          0, 4),
    ([0, 1, 2, 0, 1, 2, 1], 1, [0, 0, 1, 1, 1, 2, 2], 2, 3),
    ([1, 1, 0],             1, [0, 1, 1],             1, 2),
  ]

  def test_simple_cases(self):
    for given_nums, idx_pivot, expected_nums, expected_lt, expected_eq in self.cases:
      got_lt, got_eq = dutch_flag_partition(given_nums, idx_pivot)

      self.assertEqual(given_nums, expected_nums)
      self.assertEqual(got_lt, expected_lt)
      self.assertEqual(got_eq, expected_eq)

  @given(st.lists(st.integers(min_value=0, max_value=100), min_size=16, max_size=16), st.integers(min_value=0, max_value=15))
  def test_random(self, given_nums, idx_pivot):
    # Save the pivot now, because given_nums will get modified in-place (which
    # means given_nums[idx_pivot] could point to a different value later).
    pivot = given_nums[idx_pivot]
    got_lt, got_eq = dutch_flag_partition(given_nums, idx_pivot)
    len_given_nums = len(given_nums)

    # If all elements are the same, then that means that all of them are equal
    # to the pivot (no matter which idx_pivot we choose, we'll always end up
    # with a pivot that is the same as all other numbers in the list). This
    # means that the count of numbers equal to the pivot must be same as the
    # length of the entire list.
    if all(num == given_nums[0] for num in given_nums):
      self.assertEqual(got_eq, len_given_nums)

    # The subtotals of elements less than and equal to the pivot must never
    # exceed the length of the entire list.
    self.assertLessEqual(got_lt + got_eq, len_given_nums)

    # Check that the size of the subarray of numbers greater than the pivot
    # (which we can deduce by summing got_lt and got_eq) has
    # numbers that are indeed greater than the pivot.
    if got_lt + got_eq < len_given_nums:
      expected_gt = len_given_nums - got_lt - got_eq
      for i in range (len_given_nums - expected_gt, len_given_nums):
        self.assertGreater(given_nums[i], pivot)

if __name__ == "__main__":
  unittest.main(exit=False)
