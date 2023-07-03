from __future__ import annotations
from hypothesis import given, strategies as st
import unittest
from typing import Any, Optional
import random

import implement_stack_with_max.linked_list as lib_linked_list

class StackNaive:
    def __init__(self, *args):
        self.ll = lib_linked_list.LinkedList()
        for elt in args:
            self.push(elt)
    def push(self, elt: Any) -> None:
        if self.size() == 0:
            self.ll.insert((elt, elt))
        else:
            self.ll.insert((elt, max(elt, self.max())))
    def max(self):
        if self.size() == 0:
            return None
        node = self.ll.next
        (_, max) = node.elt
        return max
    def pop(self) -> Optional[Any]:
        node = self.ll.next
        (elt, _) = node.elt if node else (None, None)
        self.ll.delete_after()
        return elt
    def __repr__(self):
        elts = []
        node = self.ll
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        return "%s.%s(%s)" % (self.__class__.__module__,
                            self.__class__.__qualname__,
                            ", ".join(elts))
    def size(self) -> int:
        return self.ll.size()
    def __eq__(self, other) -> bool:
        return self.ll == other.ll
class Stack(StackNaive):
    def __init__(self, *args):
        self.ll_max = lib_linked_list.LinkedList()
        super().__init__(*args)
    def push(self, elt: Any) -> None:
        self.ll.insert(elt)
        if self.size() == 1:
            self.ll_max.insert((elt, 1))
            return
        (max_cur, n) = self.ll_max.next.elt
        if elt == max_cur:
            self.ll_max.delete_after()
            self.ll_max.insert((max_cur, n+1))
        elif elt > max_cur:
            self.ll_max.insert((elt, 1))
    def max(self):
        if self.size() == 0:
            return None
        (max, _n) = self.ll_max.next.elt
        return max
    def pop(self) -> Optional[Any]:
        node = self.ll.next
        elt = node.elt if node else None
        self.ll.delete_after()
        if self.size() == 0:
            self.ll_max.delete_after()
            return elt
        (max_cur, n) = self.ll_max.next.elt
        if elt == max_cur:
            self.ll_max.delete_after()
            if n > 1:
                self.ll_max.insert((max_cur, n-1))
    
        return elt
    def __repr__(self):
        elts = []
        node = self.ll_max
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        ll_repr = super().__repr__()
        ll_max_repr = "ll_max(%s)" % (", ".join(elts))
        return "%s (%s)" % (ll_repr, ll_max_repr)
    def __eq__(self, other) -> bool:
        return self.ll == other.ll \
            and self.ll_max == other.ll_max

class Test(unittest.TestCase):
    def test_init_empty_naive(self):
        stack = StackNaive()
        self.assertEqual(stack.size(), 0)
    
    def test_init_empty(self):
        stack = Stack()
        self.assertEqual(stack.size(), 0)
    
    
    def test_init_singleton_naive(self):
        stack = StackNaive(1)
        self.assertEqual(stack.size(), 1)
    
    def test_init_singleton(self):
        stack = Stack(1)
        self.assertEqual(stack.size(), 1)
    
    
    def test_init_multiple_naive(self):
        stack = StackNaive(1, 2, 3, 4, 5)
        self.assertEqual(stack.size(), 5)
    
    def test_init_multiple(self):
        stack = Stack(1, 2, 3, 4, 5)
        self.assertEqual(stack.size(), 5)
    def test_insertion_naive(self):
        stack = StackNaive()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        self.assertEqual(stack, StackNaive(1, 2, 3))
    
    def test_insertion(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        self.assertEqual(stack, Stack(1, 2, 3))
    
    
    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=0,
                    max_size=20))
    def test_insertion_random_naive(self, given_elts: list[int]):
        stack = StackNaive(*given_elts)
        self.assertEqual(stack.size(), len(given_elts))
    
    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=0,
                    max_size=20))
    def test_insertion_random(self, given_elts: list[int]):
        stack = Stack(*given_elts)
        self.assertEqual(stack.size(), len(given_elts))
    def test_size_naive(self):
        cases = [
            ([], 0),
            ([1], 1),
            ([1, 2], 2),
        ]
        for elts, expected in cases:
            stack = StackNaive(*elts)
            self.assertEqual(stack.size(), expected,
                             msg=f'{expected=}')
    
    def test_size(self):
        cases = [
            ([], 0),
            ([1], 1),
            ([1, 2], 2),
        ]
        for elts, expected in cases:
            stack = Stack(*elts)
            self.assertEqual(stack.size(), expected,
                             msg=f'{expected=}')
    def test_equality_naive(self):
        cases = [
            ([], [], True),
            ([1], [], False),
            ([1], [1], True),
            ([1], [1, 2], False),
        ]
        for xs, ys, expected in cases:
            x = StackNaive(*xs)
            y = StackNaive(*ys)
            self.assertEqual(x == y, expected,
                             msg=f'{x=} {y=}')
    
    def test_equality(self):
        cases = [
            ([], [], True),
            ([1], [], False),
            ([1], [1], True),
            ([1], [1, 2], False),
        ]
        for xs, ys, expected in cases:
            x = Stack(*xs)
            y = Stack(*ys)
            self.assertEqual(x == y, expected,
                             msg=f'{x=} {y=}')
    def test_deletion_basic_naive(self):
        stack = StackNaive(1, 2, 3)
        stack.pop()
        self.assertEqual(stack, StackNaive(1, 2),
                        msg=f'{stack=}')
    
    def test_deletion_basic(self):
        stack = Stack(1, 2, 3)
        stack.pop()
        self.assertEqual(stack, Stack(1, 2),
                        msg=f'{stack=}')
    
    
    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=1,
                    max_size=20))
    def test_deletion_random_naive(self, given_elts: list[int]):
        stack = StackNaive(*given_elts)
        deletions = random.randint(0, len(given_elts))
        for _ in range(deletions):
            stack.pop()
        self.assertEqual(stack.size(), len(given_elts) - deletions)
    
    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=1,
                    max_size=20))
    def test_deletion_random(self, given_elts: list[int]):
        stack = Stack(*given_elts)
        deletions = random.randint(0, len(given_elts))
        for _ in range(deletions):
            stack.pop()
        self.assertEqual(stack.size(), len(given_elts) - deletions)
    
    
    def test_deletion_nop_naive(self):
        stack = StackNaive()
        stack.pop()
        self.assertEqual(stack.size(), 0)
    
    def test_deletion_nop(self):
        stack = Stack()
        stack.pop()
        self.assertEqual(stack.size(), 0)
    def test_max_naive(self):
        cases = [
            ([1, 2, 3], [1, 2, 3], [2, 1]),
            ([2, 3, 10], [2, 3, 10], [3, 2]),
            ([10, 9, 8], [10, 10, 10], [10, 10]),
            ([1, 10, 5], [1, 10, 10], [10, 1]),
            ([2, 1, 2, 1], [2, 2, 2, 2], [2, 2, 2]),
            ([2, 1, 1, 1], [2, 2, 2, 2], [2, 2, 2]),
            ([2, 1, 8, 1], [2, 2, 8, 8], [8, 2, 2]),
            ([2, 1, 8, 8, 1], [2, 2, 8, 8, 8], [8, 8, 2, 2]),
        ]
        for elts, maxes, restored_maxes in cases:
            stack = StackNaive()
            for (elt, max) in zip(elts, maxes):
                stack.push(elt)
                self.assertEqual(stack.max(), max,
                                 msg=f'{stack=}')
            for restored_max in restored_maxes:
                stack.pop()
                self.assertEqual(stack.max(), restored_max,
                                 msg=f'{stack=}')
    
    def test_max(self):
        cases = [
            ([1, 2, 3], [1, 2, 3], [2, 1]),
            ([2, 3, 10], [2, 3, 10], [3, 2]),
            ([10, 9, 8], [10, 10, 10], [10, 10]),
            ([1, 10, 5], [1, 10, 10], [10, 1]),
            ([2, 1, 2, 1], [2, 2, 2, 2], [2, 2, 2]),
            ([2, 1, 1, 1], [2, 2, 2, 2], [2, 2, 2]),
            ([2, 1, 8, 1], [2, 2, 8, 8], [8, 2, 2]),
            ([2, 1, 8, 8, 1], [2, 2, 8, 8, 8], [8, 8, 2, 2]),
        ]
        for elts, maxes, restored_maxes in cases:
            stack = Stack()
            for (elt, max) in zip(elts, maxes):
                stack.push(elt)
                self.assertEqual(stack.max(), max,
                                 msg=f'{stack=}')
            for restored_max in restored_maxes:
                stack.pop()
                self.assertEqual(stack.max(), restored_max,
                                 msg=f'{stack=}')

if __name__ == "__main__":
    unittest.main(exit=False)
