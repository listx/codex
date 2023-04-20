import unittest

def parity(word):
  parity_bit = 0
  while word:
    parity_bit ^= word & 1
    word >>= 1
  return parity_bit

class TestParity(unittest.TestCase):
  def test_bf(self):
    self.assertEqual(parity(0b0), 0)
    self.assertEqual(parity(0b1), 1)
    self.assertEqual(parity(0b1011), 1)
    self.assertEqual(parity(0b1000010000), 0)
    self.assertEqual(parity(0b11), 0)
    self.assertEqual(parity(0b11111), 1)

if __name__ == "__main__":
  unittest.main(exit=False)
