import unittest

import collections
Rect = collections.namedtuple('Rect', ('x', 'y', 'width', 'height'))
def no_horizontal_overlap(a, b):
  # "L" means leftmost point
  # "R" means rightmost point
  a_L = a.x
  a_R = a.x + a.width
  b_L = b.x
  b_R = b.x + b.width
  return a_R < b_L or a_L > b_R
def no_vertical_overlap(a, b):
  # "B" means bottommost point
  # "T" means topmost point
  a_B = a.y
  a_T = a.y + a.height
  b_B = b.y
  b_T = b.y + b.height
  return a_T < b_B or a_B > b_T
def no_overlap(a, b):
  return no_horizontal_overlap(a, b) or no_vertical_overlap(a, b)
def overlapping_rectangle(a, b):
  if no_overlap(a, b):
    return None
  a_L = a.x
  a_R = a.x + a.width
  b_L = b.x
  b_R = b.x + b.width
  a_B = a.y
  a_T = a.y + a.height
  b_B = b.y
  b_T = b.y + b.height
  v_x = max(a_L, b_L)
  v_y = max(a_B, b_B)
  v_width = min(a_R, b_R) - v_x
  v_height = min(a_T, b_T) - v_y
  return Rect(v_x, v_y, v_width, v_height)

class TestOverlappingRect(unittest.TestCase):
  cases = [
    (Rect(0, 0, 1, 1), Rect(2, 2, 0, 0), None),
    (Rect(0, 0, 1, 1), Rect(2, 2, 0, 0), None),
    (Rect(0, 0, 1, 1), Rect(1, 1, 0, 0), Rect(1, 1, 0, 0)),
    (Rect(0, 0, 5, 5), Rect(1, 1, 2, 6), Rect(1, 1, 2, 4)),
  ]

  def test_simple_cases(self):
    for a, b, result in self.cases:
      self.assertEqual(overlapping_rectangle(a, b), result)
      # Also check the reverse (when we swap the order of the rectangles).
      self.assertEqual(overlapping_rectangle(b, a), result)

if __name__ == "__main__":
  unittest.main(exit=False)
