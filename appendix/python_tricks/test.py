import unittest

def is_palindrome(s: str) -> bool:
  return all(s[i] == s[~i] for i in range(len(s) // 2))

class Test(unittest.TestCase):
  def test_sort(self):
      xs = [("a", 9), ("b", 5), ("c", 1)]
      result = sorted(xs, key=lambda x: x[1])
      self.assertEqual(result, [("c", 1), ("b", 5), ("a", 9)])
  def test_indices(self):
    self.assertEqual('abcdefg'[0], 'a')
    self.assertEqual('abcdefg'[1], 'b')
    self.assertEqual('abcdefg'[-1], 'g')
    self.assertEqual('abcdefg'[-2], 'f')
    self.assertEqual('abcdefg'[-7], 'a')

    # Negative indices do not go on forever.
    with self.assertRaises(IndexError):
      'abcdefg'[-8]
  def test_slices(self):
    self.assertEqual('abcdefg'[0:2], 'ab')
    self.assertEqual('abcdefg'[2:5], 'cde')
    self.assertEqual('abcdefg'[:2], 'ab')
    self.assertEqual('abcdefg'[2:], 'cdefg')
    self.assertEqual('abcdefg'[1000:], '')
    self.assertEqual('abcdefg'[:1000], 'abcdefg')

if __name__ == "__main__":
  unittest.main(exit=False)
