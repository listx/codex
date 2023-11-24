from __future__ import annotations
from typing import Any, Callable, Optional
class MaxHeapBruteForce:
    def __init__(self):
        self.items = []
        self._count = 0

    def __len__(self):
        return self._count

    # Insertion is slow because we have to sort all items *every* time.
    def insert(self, x: Any):
        self.items.append(x)
        self.items.sort()
        self._count += 1

    def get_max(self) -> Any:
        if self._count == 0:
            raise IndexError("get from an empty heap")

        return self.items[-1]

    def pop_max(self) -> Any:
        if self._count == 0:
            raise IndexError("pop from an empty heap")

        max = self.items[-1]
        self.items = self.items[:-1]
        self._count -= 1

        return max
class MaxHeap:
    def __init__(self, size=1, get_key: Optional[Callable]=None):
        if size < 1:
            size = 1
        self.heap = [None] * size
        self._count = 0

        # get_key is a function used to return the "key" --- some aspect of the item
        # that makes it comparable with other items. If this function is not
        # specified we just return the item itself, which works for simple types
        # like integers.
        def identity(item: Any) -> Any:
            if item is None:
                raise TypeError("cannot get key of None type")
            return item

        if get_key is None:
            get_key = identity
        self._get_key = get_key
    def __len__(self):
        return self._count
    def _grow(self):
        self.heap.extend([None] * len(self.heap))

    # Used to check if we need to grow the heap.
    def _full(self) -> bool:
        return self._count + 1 == len(self.heap)
    def get_max(self) -> Any:
        # If the heap is empty, there's no max item.
        if self._count == 0:
            return None

        return self.heap[1]
    def _swap_heap_nodes(self, i: int, j: int):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    @staticmethod
    def _parent_index(i: int) -> int:
        return i >> 1

    @staticmethod
    def _left_child_index(i: int) -> int:
        return i << 1

    @staticmethod
    def _right_child_index(i: int) -> int:
        return (i << 1) + 1
    def _reheapify_up(self, i: int):
        while True:
            # We're already at the top; NOP.
            if i < 2:
                break

            parent_index = self._parent_index(i)
            parent_key = self._get_key(self.heap[parent_index])

            # Abort if we satisfy the heap condition.
            if parent_key >= self._get_key(self.heap[i]):
                break

            # Swap upward.
            self._swap_heap_nodes(parent_index, i)

            i = parent_index
    def insert(self, x: Any):
        # Grow the heap first if we're out of room.
        if self._full():
            self._grow()

        # Insert at the end of the array (just after the last item).
        self._count += 1
        self.heap[self._count] = x

        # Reheapify.
        self._reheapify_up(self._count)
    def pop_max(self) -> Any:
        max = self.get_max()

        # The last item in the array is the new root node (for now).
        self.heap[1] = self.heap[self._count]

        # Clear last item's old position in the heap (shrink the heap by 1.)
        self.heap[self._count] = None
        self._count -= 1

        # Reheapify.
        self._reheapify_down(1)

        return max
    def _reheapify_down(self, i: int):
        while True:
            # If our children would be out of bounds, abort. "Out of bounds" here
            # means outside of the tree, not the overall heap size (which includes
            # unused parts of the array).
            if self._left_child_index(i) > self._count:
                break

            left_child_index = self._left_child_index(i)
            right_child_index = self._right_child_index(i)

            # Find the bigger child. It may be that we cannot look at both child
            # indices, because one of them (the right child) might be out of bounds.
            # In that case there is only 1 possible child (the left child), and so
            # there's no need to compare children to see which one is bigger.
            if right_child_index > self._count:
                bigger_child_index = left_child_index
            else:
                left_child = self._get_key(self.heap[left_child_index])
                right_child = self._get_key(self.heap[right_child_index])

                bigger_child_index = left_child_index
                if left_child < right_child:
                    bigger_child_index = right_child_index
            bigger_child = self._get_key(self.heap[bigger_child_index])

            # If we already satisfy the heap property, stop swapping.
            if bigger_child <= self.heap[i]:
                break

            # Swap downward.
            self._swap_heap_nodes(bigger_child_index, i)

            i = bigger_child_index

class MinHeap(MaxHeap):
    def get_min(self) -> Any:
        if self._count == 0:
            return None

        return self.heap[1]

    def _reheapify_up(self, i: int):
        while True:
            if i < 2:
                break

            parent_index = self._parent_index(i)
            parent_key = self._get_key(self.heap[parent_index])

            if parent_key <= self._get_key(self.heap[i]):
                break

            self._swap_heap_nodes(parent_index, i)

            i = parent_index

    def pop_min(self) -> Any:
        min = self.get_min()

        self.heap[1] = self.heap[self._count]

        self.heap[self._count] = None
        self._count -= 1

        self._reheapify_down(1)

        return min

    def _reheapify_down(self, i: int):
        while True:
            if self._left_child_index(i) > self._count:
                break

            left_child_index = self._left_child_index(i)
            right_child_index = self._right_child_index(i)

            if right_child_index > self._count:
                smaller_child_index = left_child_index
            else:
                left_child = self._get_key(self.heap[left_child_index])
                right_child = self._get_key(self.heap[right_child_index])

                smaller_child_index = left_child_index
                if left_child > right_child:
                    smaller_child_index = right_child_index
            smaller_child = self._get_key(self.heap[smaller_child_index])

            if smaller_child >= self.heap[i]:
                break

            self._swap_heap_nodes(smaller_child_index, i)

            i = smaller_child_index
    def get_max(self):
        raise AttributeError("get_max is not supported")
    def pop_max(self):
        raise AttributeError("pop_max is not supported")
