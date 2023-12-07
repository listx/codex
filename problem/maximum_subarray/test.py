from hypothesis import given, strategies as st
import itertools
from typing import List, NamedTuple, Optional
import unittest

class SubSum(NamedTuple):
    sum: int
    # Beginning and ending indices of the original array.
    beg: int
    end: int
def brute_cubic(xs: List[int]) -> Optional[SubSum]:
    max_so_far = 0
    beg = 0
    end = 0
    found_max_so_far = False

    if not xs:
        return None

    for i in range(0, len(xs)):
        for j in range(i, len(xs)):
            subsum = sum(xs[i:j+1])
            if max_so_far < subsum:
                max_so_far = subsum
                beg = i
                end = j
                found_max_so_far = True

    if found_max_so_far:
        return SubSum(max_so_far, beg, end)

    # No max subarray found (all elements were negative).
    return None
def brute_quadratic(xs: List[int]) -> Optional[SubSum]:
    max_so_far = 0
    beg = 0
    end = 0
    found_max_so_far = False

    if not xs:
        return None

    for i in range(0, len(xs)):
        subsum = 0
        for j in range(i, len(xs)):
            subsum += xs[j]
            if max_so_far < subsum:
                max_so_far = subsum
                beg = i
                end = j
                found_max_so_far = True

    if found_max_so_far:
        return SubSum(max_so_far, beg, end)

    # No max subarray found (all elements were negative).
    return None
def brute_quadratic_alt(xs: List[int]) -> Optional[SubSum]:
    max_so_far = 0
    beg = 0
    end = 0
    found_max_so_far = False
    csums: List[int] = []

    if not xs:
        return None

    for i in range(0, len(xs)):
        if csums:
            csums.append(xs[i] + csums[i - 1])
        else:
            # "Base case" when csums is empty, because csums[0 - 1] or csums[-1]
            # will run into an IndexError.
            csums.append(xs[i])

    for i in range(0, len(xs)):
        for j in range(i, len(xs)):
            if i > 0:
                subsum = csums[j] - csums[i - 1]
            else:
                subsum = csums[j]
            if max_so_far < subsum:
                max_so_far = subsum
                beg = i
                end = j
                found_max_so_far = True

    if found_max_so_far:
        return SubSum(max_so_far, beg, end)

    # No max subarray found (all elements were negative).
    return None
def dac(xs: List[int]) -> Optional[SubSum]:
    def helper(lo, hi):
        # Zero elements. For simplicity of comparisons between M_a, M_b, and
        # M_c, we use a proxy value for None, SubSum(0, -1, -1).
        if lo > hi:
            return SubSum(0, -1, -1)

        # One element.
        if lo == hi:
            if xs[lo] <= 0:
                return SubSum(0, -1, -1)
            else:
                return SubSum(max(0, xs[lo]), lo, hi)

        # Note that the above two statements are enough to compute M_a and M_b,
        # through recursion. Now we need to compute M_c.

        # In non-arbitrary-precision integer languages, this will cause an
        # overflow because lo + hi may exceed the max allowed value of the fixed
        # size integer. To avoid this you can do "m = lo + (hi - lo // 2)"
        # instead.
        mid = (lo + hi) // 2
        M_a = helper(lo, mid)
        M_b = helper(mid + 1, hi)

        # Find max crossing over to the left.
        M_c_left_sum = 0
        sum = 0
        M_c_beg = mid
        for i in range(mid, lo - 1, -1):
            sum += xs[i]
            if sum > M_c_left_sum:
                M_c_left_sum = sum
                M_c_beg = i

        # Find max crossing over to the right.
        M_c_right_sum = 0
        sum = 0
        M_c_end = mid + 1
        for i in range(mid + 1, hi + 1):
            sum += xs[i]
            if sum > M_c_right_sum:
                M_c_right_sum = sum
                M_c_end = i

        M_c = SubSum(M_c_left_sum + M_c_right_sum, M_c_beg, M_c_end)

        if M_a.sum >= M_b.sum and M_a.sum >= M_c.sum:
            return M_a
        elif M_b.sum >= M_a.sum and M_b.sum >= M_c.sum:
            return M_b
        else:
            return M_c

    result = helper(0, len(xs) - 1)
    if result.beg == -1:
        return None
    return result
class Sums(NamedTuple):
    # Sum of all elements in the given array.
    total_sum: int

    # The max_L and max_R maximums have a requirement --- they must
    # include the first and last indices of the given array, respectively.

    # Maximum sum of subarray starting at leftmost index [0, 1, 2, ...].
    max_L: int
    # Beginning and ending indices of max_L sum.
    max_L_beg: int
    max_L_end: int

    # Maximum sum of subarray starting at rightmost index [-1, -2, -3, ...].
    max_R: int
    # Beginning and ending indices of max_R sum.
    max_R_beg: int
    max_R_end: int

    # Maximum sum of subarray without any constraints.
    max_sub: int
    # Beginning and ending indices of the max_sub sum.
    max_sub_beg: int
    max_sub_end: int

def dac_linear(xs: List[int]) -> Optional[SubSum]:
    def helper(lo, hi):
        # Zero elements. Here again we use a proxy value as before, to make
        # comparisons easier without having to deal with None values.
        if lo > hi:
            return Sums(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # One element.
        if lo == hi:
            return Sums(xs[lo],
                        xs[lo], lo, hi,
                        xs[lo], lo, hi,
                        xs[lo], lo, hi)

        # Compute M_c. We can do this quickly without having to loop to the
        # left/right of the midpoint, because we are returning additional
        # information from the recursive calls.

        mid = (lo + hi) // 2
        sums_A = helper(lo, mid)
        sums_B = helper(mid + 1, hi)

        # We have to compute the sum, max_L, and max_R of the current [lo, hi]
        # range, using the info from the left and right subarrays sums_A and sums_B.

        # The total sum is obvious --- it's the total of both halves.
        total_sum = sums_A.total_sum + sums_B.total_sum

        # Comuting max_L and max_R involve the total_sum values of the left and
        # right halves.
        if sums_A.total_sum + sums_B.max_L > sums_A.max_L:
            max_L = sums_A.total_sum + sums_B.max_L
            max_L_beg = sums_A.max_L_beg
            max_L_end = sums_B.max_L_end
        else:
            max_L = sums_A.max_L
            max_L_beg = sums_A.max_L_beg
            max_L_end = sums_A.max_L_end

        if sums_B.total_sum + sums_A.max_R > sums_B.max_R:
            max_R = sums_B.total_sum + sums_A.max_R
            max_R_beg = sums_A.max_R_beg
            max_R_end = sums_B.max_R_end
        else:
            max_R = sums_B.max_R
            max_R_beg = sums_B.max_R_beg
            max_R_end = sums_B.max_R_end

        # Finally, the maximum crossing sum (which crosses the midpoint) can be
        # computed in constant time, thanks to the constant time comparison of
        # max_L and max_R above.
        M_c = sums_A.max_R + sums_B.max_L
        cross_beg = sums_A.max_R_beg
        cross_end = sums_B.max_L_end

        # Pick the max between the largest subarray in A, B, and the crossing
        # subarray, just like for the traditional algorithm.
        if sums_A.max_sub >= sums_B.max_sub and sums_A.max_sub >= M_c:
            return Sums(total_sum,
                        max_L, max_L_beg, max_L_end,
                        max_R, max_R_beg, max_R_end,
                        sums_A.max_sub, sums_A.max_sub_beg, sums_A.max_sub_end)
        elif sums_B.max_sub >= sums_A.max_sub and sums_B.max_sub >= M_c:
            return Sums(total_sum,
                        max_L, max_L_beg, max_L_end,
                        max_R, max_R_beg, max_R_end,
                        sums_B.max_sub, sums_B.max_sub_beg, sums_B.max_sub_end)
        else:
            return Sums(total_sum,
                        max_L, max_L_beg, max_L_end,
                        max_R, max_R_beg, max_R_end,
                        M_c, cross_beg, cross_end)

    result = helper(0, len(xs) - 1)
    if result.max_sub_beg == -1:
        return None
    # For the case of [-1 , 0], the algorithm will return indices beg=1, end=1
    # to indicate that the right subarray (consisting of just [0]) has the max
    # subarray sum. But because we want to align with the brute force result
    # of returning None in the same case, we also return None.
    elif result.max_sub <= 0:
        return None
    return SubSum(result.max_sub, result.max_sub_beg, result.max_sub_end)
# Kadane's algorithm. It's named "dp" here because it is a good example of
# dynamic programming.
def dp(xs: List[int]) -> Optional[SubSum]:
    max_subarray_sum = 0
    max_subarray_beg = 0
    max_subarray_end = 0
    subarray_sum = 0
    for i, x in enumerate(xs):
        subarray_end = i
        if subarray_sum + x > x:
            subarray_sum += x
        else:
            subarray_sum = x
            subarray_beg = i

        # Keep track of the largest subarray_sum we've seen.
        if subarray_sum > max_subarray_sum:
            max_subarray_sum = subarray_sum
            max_subarray_beg = subarray_beg
            max_subarray_end = subarray_end

    if max_subarray_sum > 0:
        return SubSum(max_subarray_sum, max_subarray_beg, max_subarray_end)

    return None
def dp_running_sum(xs: List[int]) -> Optional[SubSum]:
    max_subarray_sum = 0
    max_subarray_beg = 0
    max_subarray_end = 0
    min_subarray_sum = 0
    subarray_beg = 0
    for i, running_sum in enumerate(itertools.accumulate(xs)):
        subarray_end = i
        if running_sum < min_subarray_sum:
            min_subarray_sum = running_sum
            # If we hit a new low, we know that the next iteration (if it has a
            # positive element) will be the start of a new subarray.
            subarray_beg = i + 1

        subarray_sum = running_sum - min_subarray_sum
        if subarray_sum > max_subarray_sum:
            max_subarray_sum = subarray_sum
            max_subarray_beg = subarray_beg
            max_subarray_end = subarray_end

    if max_subarray_sum > 0:
        return SubSum(max_subarray_sum, max_subarray_beg, max_subarray_end)

    return None

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty, or all negative inputs result in no answer.
        self.assertEqual(None, brute_cubic([]))
        self.assertEqual(None, brute_cubic([-1]))
        self.assertEqual(None, brute_cubic([-1, -2]))

        # Zeroes can be tricky. They should not count because they are meaningless.
        self.assertEqual(None, brute_cubic([0]))
        self.assertEqual(None, brute_cubic([0, 0]))

        # Array of all-positive integers is the entire array itself.
        self.assertEqual(SubSum(1, 0, 0), brute_cubic([1]))
        self.assertEqual(SubSum(3, 0, 1), brute_cubic([1, 2]))
        self.assertEqual(SubSum(55, 0, 9),
                         brute_cubic([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))

        # Array of positive integers, with one negative integer in the middle. We
        # should still select the entire array.
        self.assertEqual(SubSum(54, 0, 10),
                         brute_cubic([1, 2, 3, 4, 5, -1, 6, 7, 8, 9, 10]))

        # Zeroes are included in the subarray sum.
        self.assertEqual(SubSum(2, 0, 3),
                         brute_cubic([1, 0, 0, 1]))

        # Examples used earlier up in the discussion.
        want_xs = [
            (SubSum(6, 3, 6), [-2, 1, -3, 4, -1, 2, 1, -5, 4]),
            (SubSum(6, 1, 3), [-1, 1, 2, 3, -1, -2, -1, 1, 1, 1, -1]),
            (SubSum(7, 1, 8), [-1, 1, 2, 3, -1, -1, 1, 1, 1, -1]),
            (SubSum(15, 5, 7), [-1, 1,  0, 7, -9, 7, 1, 7, -10, 3, 1, 1, -1])
        ]
        for want, xs in want_xs:
            self.assertEqual(want, brute_cubic(xs))
            self.assertEqual(want, brute_quadratic(xs))
            self.assertEqual(want, brute_quadratic_alt(xs))
            self.assertEqual(want, dac(xs))
            self.assertEqual(want, dac_linear(xs))
            self.assertEqual(want, dp(xs))
            self.assertEqual(want, dp_running_sum(xs))
    @given(st.lists(st.integers(min_value=-50, max_value=50),
                    min_size=0,
                    max_size=50))
    def test_random(self, xs: List[int]):
        result_brute = brute_cubic(xs)

        # Do the solutions agree with each other?
        self.assertEqual(result_brute, brute_quadratic(xs))
        self.assertEqual(result_brute, brute_quadratic_alt(xs))
        self.assertEqual(result_brute, dp_running_sum(xs))

        def helper(want, algos):
            for algo in algos:
                # The non-brute solutions could choose a different subarray of
                # an equal sum, so just check that the sums agree, and that the
                # algo's chosen indices do check out.
                got = algo(xs)
                if want is not None and got is not None:
                    self.assertIsNotNone(got)
                    self.assertEqual(want.sum, got.sum)
                    self.assertEqual(want.sum,
                                    sum(xs[got.beg:got.end + 1]))
                elif want is None and got is None:
                    pass
                else:
                    # Fail the test, because the results don't agree on None-ness.
                    # But instead of failing with self.fail(), give the most
                    # information possible by doing an assertion.
                    self.assertEqual(want, got)

        helper(result_brute, [dac, dac_linear, dp, dp_running_sum])

if __name__ == "__main__":
    unittest.main(exit=False)
