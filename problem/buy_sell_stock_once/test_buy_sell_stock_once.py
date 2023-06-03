from hypothesis import given, strategies as st
import unittest

from typing import Optional

def brute_force(prices: list[int]) -> Optional[tuple[int, int, int]]:
  if not prices:
    return None

  max_profit_so_far = 0
  for buy_date, price_buy in enumerate(prices):
    for sell_date in range(buy_date + 1, len(prices)):
      profit = prices[sell_date] - price_buy
      if profit > max_profit_so_far:
        max_profit_so_far = profit
        transaction_dates = (buy_date, sell_date, profit)

  if max_profit_so_far:
    return transaction_dates

  # If no profitable trade found, return None.
  return None

def optimal(prices: list[int]) -> Optional[tuple[int, int, int]]:
  if not prices:
    return None

  min_price_so_far = float('inf')
  max_profit = 0

  for date, price in enumerate(prices):
    if price < min_price_so_far:
      buy_date = date
      min_price_so_far = min(price, min_price_so_far)

    max_profit_if_sell_now = price - min_price_so_far
    max_profit_prev = max_profit
    max_profit = max(int(max_profit_if_sell_now), max_profit)

    if max_profit > max_profit_prev:
      transaction_dates = (buy_date, date, max_profit)

  if max_profit:
    return transaction_dates

  # If no profitable trade found, return None.
  return None

class Test(unittest.TestCase):
  cases = [
    ([],                      None),
    ([0],                     None),
    ([0, 0, 0, 0],            None),
    ([3, 2, 1],               None),
    ([5, 25, 100, 50],        (0, 2, 95)),
    ([5, 25, 100, 1, 50, 99], (3, 5, 98)),
  ]

  def test_simple_cases(self):
    for given_prices, expected in self.cases:
      self.assertEqual(brute_force(given_prices), expected)
      self.assertEqual(optimal(given_prices), expected)

  @given(st.lists(st.integers(min_value=1, max_value=100), min_size=0,
                  max_size=14))
  def test_random(self, given_prices: list[int]):
    got = brute_force(given_prices)

    # If the prices were not always decreasing, then there must have been some
    # optimum buy/sell date.
    if given_prices and max(given_prices) > given_prices[0]:
      self.assertNotEqual(got, None)

    # Check that the optimal solution agrees with brute force.
    self.assertEqual(optimal(given_prices), got)

if __name__ == "__main__":
  unittest.main(exit=False)
