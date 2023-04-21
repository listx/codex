from hypothesis import given, strategies as st

import unittest

def brute_force_1(word):
  parity_bit = 0
  while word:
    parity_bit ^= word & 1
    word >>= 1
  return parity_bit

def brute_force_2(word):
  parity_bit = 0
  while word:
    parity_bit ^= 1
    word &= word - 1
  return parity_bit

def brute_force_3(word):
  word ^= word >> 32
  word ^= word >> 16
  word ^= word >> 8
  word ^= word >> 4
  word ^= word >> 2
  word ^= word >> 1
  return word & 1

def brute_force_4(word):
  word ^= word >> 32
  word ^= word >> 16
  word ^= word >> 8
  word ^= word >> 4
  word = 0x6996 >> (word & 0xf)
  return word & 1


PARITY = [brute_force_3(word) for word in range(1 << 16)]
MASK_SIZE = 16
BIT_MASK = 0xffff

def caching(word):
  a = PARITY[word >> (3 * MASK_SIZE)]
  b = PARITY[(word >> (2 * MASK_SIZE)) & BIT_MASK]
  c = PARITY[(word >> MASK_SIZE) & BIT_MASK]
  d = PARITY[word & BIT_MASK]
  return a ^ b ^ c ^ d

def caching_xor(word):
  word ^= word >> 32
  word ^= word >> 16
  return PARITY[word & BIT_MASK]

def black_magic(word):
  word ^= word >> 1
  word ^= word >> 2
  word &= 0x1111111111111111
  word *= 0x1111111111111111
  return (word >> 60) & 1

class TestParity(unittest.TestCase):
  cases = [
    (0b0, 0),
    (0b1, 1),
    (0b1011, 1),
    (0b1000010000, 0),
    (0b11, 0),
    (0b11111, 1),
    (0b1000000000000000000000000000000000000000000000000000000000000000, 1),
    (0b1000000000000000000000000000000000000000100000000000000000000000, 0),
  ]

  def test_simple_cases(self):
    for word, parity_bit in self.cases:
      self.assertEqual(brute_force_1(word), parity_bit)
      self.assertEqual(brute_force_2(word), parity_bit)
      self.assertEqual(brute_force_3(word), parity_bit)
      self.assertEqual(brute_force_4(word), parity_bit)
      self.assertEqual(caching(word), parity_bit)
      self.assertEqual(caching_xor(word), parity_bit)
      self.assertEqual(black_magic(word), parity_bit)

  @given(st.integers(min_value=0, max_value=((1<<64) - 1)))
  def test_random(self, word):
    parity_bit = black_magic(word)
    self.assertEqual(brute_force_1(word), parity_bit)
    self.assertEqual(brute_force_2(word), parity_bit)
    self.assertEqual(brute_force_3(word), parity_bit)
    self.assertEqual(brute_force_4(word), parity_bit)
    self.assertEqual(caching(word), parity_bit)
    self.assertEqual(caching_xor(word), parity_bit)

if __name__ == "__main__":
  unittest.main(exit=False)
