import heapq
from hypothesis import given, strategies as st
from typing import List
import unittest

from .heap import MaxHeapBruteForce, MaxHeap, MinHeap

class Test(unittest.TestCase):
    def test_init_bf(self):
        h = MaxHeapBruteForce()
        self.assertEqual(len(h), 0)
    def test_get_max_bf(self):
        h = MaxHeapBruteForce()
        self.assertEqual(len(h), 0)
        self.assertRaises(IndexError, h.get_max)
        h.insert(1)
        self.assertEqual(h.get_max(), 1)
        h.insert(2)
        self.assertEqual(h.get_max(), 2)
    def test_insertion_bf(self):
        h = MaxHeapBruteForce()
        h.insert(1)
        h.insert(2)
        h.insert(3)
        self.assertEqual(len(h), 3)
    def test_pop_max_bf(self):
        h = MaxHeapBruteForce()
        h.insert(1)
        h.insert(2)
        h.insert(3)
        self.assertEqual(len(h), 3)

        x = h.pop_max()
        self.assertEqual(x, 3)
        self.assertEqual(len(h), 2)

        x = h.pop_max()
        self.assertEqual(x, 2)
        self.assertEqual(len(h), 1)

        x = h.pop_max()
        self.assertEqual(x, 1)
        self.assertEqual(len(h), 0)
    @given(st.lists(st.integers(min_value=1, max_value=1000),
                    min_size=1,
                    max_size=50))
    def test_heap_sort(self, to_insert: list[int]):
        max_heap_bf = MaxHeapBruteForce()
        max_heap_optimal = MaxHeap()
        self.assertEqual(len(max_heap_bf), len(max_heap_optimal))

        # Populate heaps.
        for item in to_insert:
            max_heap_bf.insert(item)
            max_heap_optimal.insert(item)
        self.assertEqual(len(max_heap_bf), len(max_heap_optimal))

        # Drain heaps.
        output_bf = []
        output_optimal = []
        for _ in range(len(to_insert)):
            x = max_heap_bf.pop_max()
            y = max_heap_optimal.pop_max()
            output_bf.append(x)
            output_optimal.append(y)
        self.assertEqual(output_bf, output_optimal)
        self.assertEqual(len(max_heap_bf), len(max_heap_optimal))

        # Are the outputs sorted (in reverse, because it's a max-heap)?
        s = list(sorted(to_insert))
        self.assertEqual(s, list(reversed(output_bf)))
        self.assertEqual(s, list(reversed(output_optimal)))
    @given(st.lists(st.integers(min_value=1, max_value=1000),
                    min_size=1,
                    max_size=50))
    def test_min_heap(self, to_insert: list[int]):
        min_heap = MinHeap()
        min_heap_std: List[int] = []

        # Populate heaps.
        for item in to_insert:
            min_heap.insert(item)
            heapq.heappush(min_heap_std, item)
        self.assertEqual(len(min_heap), len(min_heap_std))

        # Drain heaps.
        output = []
        output_std = []
        for _ in range(len(to_insert)):
            x = min_heap.pop_min()
            y = heapq.heappop(min_heap_std)
            output.append(x)
            output_std.append(y)

        # Check drained output (should be in agreement with heapq output).
        self.assertEqual(output, output)
        self.assertEqual(len(min_heap), len(min_heap_std))

if __name__ == "__main__":
    unittest.main(exit=False)
