from hypothesis import given, strategies as st
import unittest

def brute_force(word):
  parity_bit = 0
  while word:
    parity_bit ^= word & 1
    word >>= 1
  return parity_bit

def clear_lsb(word):
  parity_bit = 0
  while word:
    parity_bit ^= 1
    word &= word - 1
  return parity_bit

def xor_fold(word):
  word ^= word >> 32
  word ^= word >> 16
  word ^= word >> 8
  word ^= word >> 4
  word ^= word >> 2
  word ^= word >> 1
  return word & 1

def xor_fold_lookup(word):
  word ^= word >> 32
  word ^= word >> 16
  word ^= word >> 8
  word ^= word >> 4
  word = 0x6996 >> (word & 0xf)
  return word & 1


PARITY = [xor_fold(word) for word in range(1 << 16)]

def caching(word):
  a = PARITY[word >> 48]
  b = PARITY[word >> 32 & 0xffff]
  c = PARITY[word >> 16 & 0xffff]
  d = PARITY[word       & 0xffff]
  return a ^ b ^ c ^ d

def xor_fold_caching(word):
  word ^= word >> 32
  word ^= word >> 16
  return PARITY[word & 0xffff]

def xor_fold_nibbles(word):
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
      self.assertEqual(brute_force(word), parity_bit)
      self.assertEqual(clear_lsb(word), parity_bit)
      self.assertEqual(xor_fold(word), parity_bit)
      self.assertEqual(xor_fold_lookup(word), parity_bit)
      self.assertEqual(caching(word), parity_bit)
      self.assertEqual(xor_fold_caching(word), parity_bit)
      self.assertEqual(xor_fold_nibbles(word), parity_bit)

  @given(st.integers(min_value=0, max_value=((1<<64) - 1)))
  def test_random(self, word):
    parity_bit = xor_fold_nibbles(word)
    self.assertEqual(brute_force(word), parity_bit)
    self.assertEqual(clear_lsb(word), parity_bit)
    self.assertEqual(xor_fold(word), parity_bit)
    self.assertEqual(xor_fold_lookup(word), parity_bit)
    self.assertEqual(caching(word), parity_bit)
    self.assertEqual(xor_fold_caching(word), parity_bit)
    self.assertEqual(xor_fold_nibbles(word), parity_bit)

if __name__ == "__main__":
  unittest.main(exit=False)
