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

def caching(word):
  # TODO
  return

class TestParity(unittest.TestCase):
  cases = [
    (0b0, 0),
    (0b1, 1),
    (0b1011, 1),
    (0b1000010000, 0),
    (0b11, 0),
    (0b11111, 1),
  ]

  def test_brute_force(self):
    for word, parity_bit in self.cases:
      self.assertEqual(brute_force_1(word), parity_bit)
      self.assertEqual(brute_force_2(word), parity_bit)
      self.assertEqual(brute_force_3(word), parity_bit)
      self.assertEqual(caching(word), parity_bit)

if __name__ == "__main__":
  unittest.main(exit=False)
