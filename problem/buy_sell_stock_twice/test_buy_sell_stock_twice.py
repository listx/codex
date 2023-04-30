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

class Test(unittest.TestCase):
  cases = [
    ([],                          None),
    ([0],                         None),
    ([0, 0, 0, 0],                None),
    ([3, 2, 1],                   None),
    ([5, 25, 100, 50],            (TXN(0, 2, 95), None)),
    ([5, 25, 100, 1, 50, 99],     (TXN(0, 2, 95), TXN(3, 5, 98))),
    ([1, 2, 3, 4, 5, 1, 5, 1, 4], (TXN(0, 4, 4),  TXN(5, 6, 4))),
  ]

  def test_simple_cases(self):
    for given_prices, expected in self.cases:
      self.assertEqual(brute_force_maybe_sell_twice(given_prices), expected)

  @given(st.lists(st.integers(min_value=1, max_value=100), min_size=0, max_size=14))
  def test_random(self, given_prices: list[int]):
    gotSingle = brute_force(given_prices)
    gotDouble = brute_force_maybe_sell_twice(given_prices)

    # If we say that we should buy/sell twice, then it must be because we can
    # make more money than buying and selling only once.
    if (gotSingle is not None
        and gotDouble is not None
        and gotDouble[0] is not None
        and gotDouble[1] is not None):
      self.assertGreater(gotDouble[0].profit + gotDouble[1].profit, gotSingle.profit)

if __name__ == "__main__":
  unittest.main(exit=False)
