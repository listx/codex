import bisect
from hypothesis import given, strategies as st
from typing import List
import unittest

def brute1(xs: List[int], ys: List[int]) -> List[int]:
    result = list(set(xs) & set(ys))
    result.sort()
    return result
def brute2(xs: List[int], ys: List[int]) -> List[int]:
    result = []
    for x in xs:
        # Go to next x if it's a dupe.
        if x in result:
            continue
        for y in ys:
            # Similarly, skip over dupes in y.
            if y in result:
                continue
            if x == y:
                result.append(x)
                break
    return result
def better(xs: List[int], ys: List[int]) -> List[int]:
    def has(needle: int, haystack: List[int]):
        i = bisect.bisect_left(haystack, needle)
        return i < len(haystack) and haystack[i] == needle

    result = []
    for i, x in enumerate(xs):
        # Only add this element if it is inside ys (intersection confirmed) and
        # if it is not a duplicate.
        if has(x, ys) and (i == 0 or x != xs[i - 1]):
            result.append(x)
    return result
def optimal(xs: List[int], ys: List[int]) -> List[int]:
    i = 0
    j = 0
    result = []

    while i < len(xs) and j < len(ys):
        # Skip over non-matching items (including duplicates).
        if xs[i] < ys[j]:
            i += 1
        elif xs[i] > ys[j]:
            j += 1
        # We have a match.
        else:
            # Again, avoid adding the same item twice into the result.
            if i == 0 or xs[i] != xs[i - 1]:
                result.append(xs[i])

            # We've consumed the information pointed to by both pointers, so
            # they are useless now. Advance the pointers to fetch new content
            # for the next iteration.
            i += 1
            j += 1

    return result

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty inputs.
        xs = []
        ys = []
        result = brute1(xs, ys)
        self.assertEqual(result, [])

        # Basic examples, as described in the problem statement.
        xs = [1, 2]
        ys = [3, 4]
        result = brute1(xs, ys)
        self.assertEqual(result, [])
        xs = [1, 1, 1, 2]
        ys = [1, 2, 2, 3]
        result = brute1(xs, ys)
        self.assertEqual(result, [1, 2])
    @given(st.lists(st.integers(min_value=1, max_value=50),
                    min_size=1,
                    max_size=50),
           st.lists(st.integers(min_value=1, max_value=50),
                    min_size=1,
                    max_size=50))
    def test_random(self, xs: List[int], ys: List[int]):
        xs.sort()
        ys.sort()

        result_brute1 = brute1(xs, ys)
        result_brute2 = brute2(xs, ys)
        result_better = better(xs, ys)
        result_optimal = optimal(xs, ys)

        # Do the solutions agree with each other?
        self.assertEqual(result_brute1, result_brute2)
        self.assertEqual(result_brute2, result_better)
        self.assertEqual(result_better, result_optimal)

if __name__ == "__main__":
    unittest.main(exit=False)
