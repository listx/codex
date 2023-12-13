from hypothesis import given, strategies as st
from typing import Dict, List
import unittest

def brute_exponential(amount: int, coins: List[int]) -> int:
    combinations = 0

    # Assume that coins is sorted already (e.g., [1, 5, 10, 25]).
    variables = [0] * len(coins)

    def maxed_out(variables):
        bools = [False] * len(variables)
        for i, coin in enumerate(coins):
            if variables[i] * coin >= amount:
                bools[i] = True
        return all(bools)

    def increment(variables):
        for i, coin in enumerate(coins):
            if variables[i] * coin < amount:
                variables[i] += 1
                # If we increment a higher base, we need to reset all lower
                # bases.
                if i > 0:
                    for x in range(i):
                        variables[x] = 0
                break
        return variables

    while not maxed_out(variables):
        variables = increment(variables)
        got = 0
        for i, coin in enumerate(coins):
            got += (variables[i] * coin)

        if got == amount:
            combinations += 1

    return combinations
def brute_dfs(amount: int, coins: List[int]) -> int:
    cache: Dict[int, int] = {}

    def dfs(amt, i):
        if i == len(coins):
            return 0
        if amt - coins[i] == 0:
            return 1
        if amt < 0:
            return 0
        if (amt, i) in cache:
            return cache[(amt, i)]

        # Include all ways to reach an amount that is smaller than the current
        # coin value, but using the same coin (index "i" is unchanged in this
        # call).
        combos = dfs(amt - coins[i], i)

        # Include all ways to get the current amount using other coins other
        # than this one (because using the current one does not get us to zero
        # (if it did, we would've returned early above)).
        combos += dfs(amt, i + 1)

        # Remember the result in the cache (memoization).
        cache[(amt, i)] = combos

        return combos

    return dfs(amount, 0)
def dp(amount: int, coins: List[int]) -> int:
    # These are special condition to match the behavior of our brute force and
    # DFS solutions.
    if not coins:
        return 0
    if not amount:
        return 0

    table = [[1] + [0] * amount
             for _ in coins]

    for i, coin in enumerate(coins):
        for amt in range(1, amount + 1):
            with_coin = table[i][amt - coin] if amt >= coin else 0
            without_coin = table[i - 1][amt] if i > 0 else 0
            table[i][amt] = with_coin + without_coin

    return table[-1][amount]
def dp_optimized(amount: int, coins: List[int]) -> int:
    # These are special condition to match the behavior of our brute force and
    # DFS solutions.
    if not coins:
        return 0
    if not amount:
        return 0

    table = [1] + [0] * amount

    for coin in coins:
        for amt in range(amount + 1):
            # Skip over negative sums.
            if amt - coin < 0:
                continue
            table[amt] += table[amt - coin]

    return table[amount]

class Test(unittest.TestCase):
    def test_basic(self):
        cases = [
            # No combination to make sum of 0, with no coins.
            (0,     0,      []),
            # No combination to make sum of 0, with smallest possible coin (penny).
            (0,     0,      [1]),
            # Some basic cases.
            (1,     1,      [1]),
            (4,     12,     [2, 3, 7]),
            # Some values from Table 7 in the text.
            (9,     20,     [1, 5, 10, 25]),
            (18,    30,     [1, 5, 10, 25]),
            (24,    35,     [1, 5, 10, 25]),
            (31,    40,     [1, 5, 10, 25]),
            (39,    45,     [1, 5, 10, 25]),
            (49,    50,     [1, 5, 10, 25]),
            (293,   100,    [1, 5, 10, 25, 50, 100]),
        ]
        for want, amount, coins in cases:
            self.assertEqual(want, brute_exponential(amount, coins))
            self.assertEqual(want, brute_dfs(amount, coins))
            self.assertEqual(want, dp(amount, coins))
            self.assertEqual(want, dp_optimized(amount, coins))
    @given(st.integers(min_value=0, max_value=50),
           st.lists(st.integers(min_value=1, max_value=50),
                    min_size=0,
                    max_size=4,
                    unique=True))
    def test_random(self, amount: int, coins: List[int]):
        # Sort the coins.
        coins.sort()

        result_brute = brute_exponential(amount, coins)

        # Do the solutions agree with each other?
        self.assertEqual(result_brute, brute_dfs(amount, coins))
        self.assertEqual(result_brute, dp(amount, coins))
        self.assertEqual(result_brute, dp_optimized(amount, coins))

if __name__ == "__main__":
    unittest.main(exit=False)
