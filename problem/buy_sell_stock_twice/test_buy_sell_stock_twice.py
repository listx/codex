from hypothesis import given, strategies as st
import unittest

from typing import Optional

from typing import Optional

import collections
TXN = collections.namedtuple('TXN', ('buy_date', 'sell_date', 'profit'))
def brute_force(prices: list[int]) -> Optional[TXN]:
  if not prices:
    return None

  max_profit_so_far = 0
  for buy_date, price_buy in enumerate(prices):
    for sell_date in range(buy_date + 1, len(prices)):
      profit = prices[sell_date] - price_buy
      if profit > max_profit_so_far:
        max_profit_so_far = profit
        transaction_dates = TXN(buy_date, sell_date, profit)

  if max_profit_so_far:
    return transaction_dates

  # If no profitable trade found, return None.
  return None
def brute_force_sublists(prices: list[int]
  ) -> Optional[tuple[TXN, TXN]]:

  # There are 2 sublists and each one must have at least 2 items.
  if len(prices) < 4:
    return None

  # Divide up prices into sublists.
  sublists = [(prices[0:i], prices[i:])
   for i in range(0, len(prices))
   if i > 1 and len(prices) - i > 1]

  txn_dates = None
  max_sell_twice = 0
  for list1, list2 in sublists:
    txn1 = brute_force(list1)
    txn2 = brute_force(list2)
    if txn1 is not None and txn2 is not None:
      if txn1.profit + txn2.profit > max_sell_twice:
        # The indices (dates) for txn2 are wrong because list2 will start at its
        # own index 0. So we need to give the dates an offset.
        txn2 = txn2._replace(buy_date = txn2.buy_date + len(list1))
        txn2 = txn2._replace(sell_date = txn2.sell_date + len(list1))

        txn_dates = (txn1, txn2)
        max_sell_twice = max(txn1.profit + txn2.profit,
                             max_sell_twice)

  if max_sell_twice:
    return txn_dates

  return None
def brute_force_maybe_sell_twice(prices: list[int]
  ) -> Optional[tuple[Optional[TXN], Optional[TXN]]]:

  txn = brute_force(prices)
  txn_pair = brute_force_sublists(prices)

  # If there's no way to make a profit with a single sale, give up.
  if txn is None:
    return None

  if txn_pair is None:
    return txn, None

  max_sell_twice = txn_pair[0].profit + txn_pair[1].profit

  if max_sell_twice > txn.profit:
    return txn_pair

  # If the max_sell_twice profit wasn't bigger, then the best we got is the one
  # from the one sale in txn.
  return txn, None
def two_pass_maybe_sell_twice(prices: list[int]
  ) -> Optional[tuple[Optional[TXN], Optional[TXN]]]:
  if len(prices) < 2:
    return None

  min_price_so_far = float('inf')
  max_profit_sell_once = 0
  txn1 = None
  txn2 = None
  profit_txn1 = [TXN(-1, -1, -1)] * len(prices)

  for date, price in enumerate(prices):
    if price < min_price_so_far:
      buy_date = date
      min_price_so_far = min(price, min_price_so_far)

    max_profit_if_sell_now = price - min_price_so_far

    if max_profit_if_sell_now > max_profit_sell_once:
      max_profit_sell_once = max(int(max_profit_if_sell_now), max_profit_sell_once)
      txn1 = TXN(buy_date, date, max_profit_sell_once)

    if txn1 is not None:
      profit_txn1[date] = txn1

  # Our current understanding of the max possible profit is by looking at one
  # buy and one sell.
  max_profit = max_profit_sell_once

  # Now consider a second sale.
  max_price_so_far = 0
  for date, price in reversed(list(enumerate(prices[2:], 2))):
    if price >= max_price_so_far:
      sell_date = date
      max_price_so_far = max(max_price_so_far, price)

    profit_txn2 = max_price_so_far - price

    if profit_txn2 <= 0:
      continue

    max_profit_sell_twice = profit_txn1[date - 1].profit + profit_txn2
    if max_profit_sell_twice < max_profit:
      continue

    # If selling once or twice gives us the same profit, then just sell once.
    if txn1 is not None and txn1.profit == max_profit_sell_twice:
      continue

    max_profit = max(max_profit, max_profit_sell_twice)
    txn1 = profit_txn1[date - 1]
    txn2 = TXN(date, sell_date, profit_txn2)

  if txn1 is None:
    return None

  return txn1, txn2

class Test(unittest.TestCase):
  cases = [
    ([],                          None),
    ([0],                         None),
    ([0, 0, 0, 0],                None),
    ([3, 2, 1],                   None),
    ([5, 25, 100, 50],            (TXN(0, 2, 95), None)),
    ([5, 25, 100, 1, 50, 99],     (TXN(0, 2, 95), TXN(3, 5, 98))),
    ([1, 2, 3, 4, 5, 1, 5, 1, 4], (TXN(0, 4, 4),  TXN(5, 6, 4))),
    ([1, 3, 2, 1, 3],             (TXN(0, 1, 2),  TXN(3, 4, 2))),
    ([1, 2, 1, 1, 2],             (TXN(0, 1, 1),  TXN(2, 4, 1))),
    ([1, 1, 1, 2],                (TXN(0, 3, 1),  None)),
    ([1, 2, 2, 3],                (TXN(0, 3, 2),  None)),
    ([3, 5, 2, 1, 3],             (TXN(0, 1, 2),  TXN(3, 4, 2))),
  ]

  def test_simple_cases(self):
    for given_prices, expected in self.cases:
      self.assertEqual(brute_force_maybe_sell_twice(given_prices), expected,
                       msg=f'{given_prices=}')
      self.assertEqual(two_pass_maybe_sell_twice(given_prices), expected,
                       msg=f'{given_prices=}')

  @given(st.lists(st.integers(min_value=1, max_value=100), min_size=0, max_size=14))
  def test_random(self, given_prices: list[int]):
    got_sell_once = brute_force(given_prices)
    got_maybe_sell_twice = brute_force_maybe_sell_twice(given_prices)

    # If we say that we should buy/sell twice, then it must be because we can
    # make more money than buying and selling only once.
    if (got_sell_once is not None
        and got_maybe_sell_twice is not None
        and got_maybe_sell_twice[0] is not None
        and got_maybe_sell_twice[1] is not None):
      self.assertGreater(
        got_maybe_sell_twice[0].profit + got_maybe_sell_twice[1].profit,
        got_sell_once.profit)

    # Check that the other solutions agree with brute force.
    self.assertEqual(two_pass_maybe_sell_twice(given_prices),
                     got_maybe_sell_twice)

if __name__ == "__main__":
  unittest.main(exit=False)
