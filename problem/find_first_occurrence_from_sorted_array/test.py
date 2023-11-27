import bisect
from hypothesis import given, strategies as st
from typing import List, Optional
import unittest

def find_first_occurrence_brute_force(haystack: List[int],
                                      needle: int) -> Optional[int]:
    for i, item in enumerate(haystack):
        if item == needle:
            return i
    return None
def find_first_occurrence_optimal(haystack: List[int], needle: int) -> Optional[int]:
    left = 0
    right = len(haystack) - 1
    result = None

    # Search the entire haystack to find the first occurrence.
    while left <= right:
        mid = (left + right) // 2

        # Reduce the search space by 1/2 on every iteration. If the midpoint is
        # lower than the needle, move the left bound to just past the middle.
        # Otherwise (including the case where the midpoint is equal to or
        # greater than the needle), move the right bound to just below the
        # middle. This way we can continue to search even if we get a search
        # hit.
        if haystack[mid] < needle:
            left = mid + 1
        else:
            right = mid - 1

        # We got a search hit; record the location for now, but don't break the
        # loop because we want to continue searching until the left/right
        # pointers cross.
        if haystack[mid] == needle:
            result = mid

    return result
def find_first_occurrence_pythonic(haystack: List[int], needle: int) -> Optional[int]:
    result = None

    try:
        i = haystack.index(needle)
    except ValueError:
        pass
    else:
        result = i

    return result

def find_first_occurrence_pythonic_bisect(haystack: List[int],
                                          needle: int) -> Optional[int]:
    result = None

    i = bisect.bisect_left(haystack, needle)
    if i != len(haystack) and haystack[i] == needle:
        result = i

    return result

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty search space.
        haystack = []
        needle = 1
        result = find_first_occurrence_brute_force(haystack, needle)
        self.assertEqual(result, None)

        # Simplest search hit.
        haystack = [1]
        needle = 1
        result = find_first_occurrence_brute_force(haystack, needle)
        self.assertEqual(result, 0)

        # Basic examples, as described in the problem statement.
        haystack = [1, 2, 4, 7, 8]
        needle = 7
        result = find_first_occurrence_brute_force(haystack, needle)
        self.assertEqual(result, 3)
        haystack = [1]
        needle = 2
        result = find_first_occurrence_brute_force(haystack, needle)
        self.assertEqual(result, None)

        # Pathological case.
        haystack = [1] * 100
        needle = 1
        result = find_first_occurrence_brute_force(haystack, needle)
        self.assertEqual(result, 0)
    @given(st.lists(st.integers(min_value=1, max_value=50),
                    min_size=1,
                    max_size=50),
           st.integers(min_value=1, max_value=50))
    def test_random(self, haystack: List[int], needle: int):
        # The input has to be sorted, per the rules of the problem.
        haystack.sort()

        result_bf = find_first_occurrence_brute_force(haystack, needle)
        result_optimal = find_first_occurrence_optimal(haystack, needle)
        result_pythonic = find_first_occurrence_pythonic(haystack, needle)
        result_pythonic_bisect = find_first_occurrence_pythonic_bisect(haystack, needle)

        # Do the solutions agree with each other?
        self.assertEqual(result_bf, result_optimal)
        self.assertEqual(result_optimal, result_pythonic)
        self.assertEqual(result_pythonic, result_pythonic_bisect)

if __name__ == "__main__":
    unittest.main(exit=False)
