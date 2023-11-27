from collections.abc import Iterator
import copy
import heapq
from hypothesis import given, strategies as st
from typing import List, Tuple
import unittest

def merge_brute_force(streams: List[Iterator[int]]) -> Iterator[int]:
    buf = []
    for stream_id, stream in enumerate(streams):
        item = next(stream, None)
        if item is not None:
            buf.append((item, stream_id))

    while buf:
        buf.sort() # Expensive!
        item, stream_id = buf[0]
        buf = buf[1:]

        yield item

        next_item = next(streams[stream_id], None)
        if next_item is not None:
            buf.append((next_item, stream_id))
def merge_optimal(streams: List[Iterator[int]]) -> Iterator[int]:
    buf: List[Tuple[int, int]] = []
    for stream_id, stream in enumerate(streams):
        item = next(stream, None)
        if item is not None:
            heapq.heappush(buf, (item, stream_id))

    while buf:
        item, stream_id = heapq.heappop(buf)

        yield item

        next_item = next(streams[stream_id], None)
        if next_item is not None:
            heapq.heappush(buf, (next_item, stream_id))

# Utilities.
def drain(stream: Iterator[int]) -> List[int]:
    return [x for x in stream]

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty streams result in nothing.
        s1 = iter([])
        s2 = iter([])
        s3 = iter([])
        streams = [s1, s2, s3]
        result = drain(merge_brute_force(streams))
        self.assertEqual(result, [])

        # Only one stream has content.
        s1 = iter([])
        s2 = iter([1, 2, 3])
        s3 = iter([])
        streams = [s1, s2, s3]
        result = drain(merge_brute_force(streams))
        self.assertEqual(result, [1, 2, 3])

        # Basic example, as described in the problem statement.
        s1 = iter([0, 1, 2, 3])
        s2 = iter([5, 6, 7])
        s3 = iter([0, 2, 4])
        streams = [s1, s2, s3]
        result = drain(merge_brute_force(streams))
        self.assertEqual(result, [0, 0, 1, 2, 2, 3, 4, 5, 6, 7])
    @given(st.lists(st.lists(st.integers(min_value=1, max_value=1000),
                    min_size=1,
                    max_size=50), # Max number of items in a stream.
           min_size=1,
           max_size=5)) # Max number of streams.
    def test_random(self, streams: List[List[int]]):
        # Sort values inside each stream first.
        iters = []
        for stream in streams:
            stream.sort()
            iters.append(iter(stream))

        # Create an identical set of streams (will be drained by the optimal
        # solution).
        iters_2 = copy.deepcopy(iters)

        result_bf = drain(merge_brute_force(iters))
        result_optimal = drain(merge_optimal(iters_2))
        self.assertEqual(result_bf, result_optimal)

if __name__ == "__main__":
    unittest.main(exit=False)
