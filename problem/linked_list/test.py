from __future__ import annotations
from hypothesis import given, strategies as st
import unittest
import random

from .linked_list import LinkedList

class Test(unittest.TestCase):
    def test_init_empty(self):
        linked_list = LinkedList()
        self.assertEqual(linked_list.size(), 0)

    def test_init_singleton(self):
        linked_list = LinkedList(1)
        self.assertEqual(linked_list.size(), 1)

    def test_init_multiple(self):
        linked_list = LinkedList(1, 2, 3, 4, 5)
        self.assertEqual(linked_list.size(), 5)
        # Head node holds nothing.
        self.assertEqual(linked_list.elt, None)
        self.assertEqual(linked_list.next.elt, 1)
    def test_insertion_head_without_data(self):
        linked_list = LinkedList(1, 2, 3)
        self.assertEqual(linked_list, LinkedList(1, 2, 3))

    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=0,
                    max_size=20))
    def test_insertion_random(self, given_elts: list[int]):
        linked_list = LinkedList(*given_elts)
        self.assertEqual(linked_list.size(), len(given_elts))
    def test_size(self):
        cases = [
            ([], 0),
            ([1], 1),
            ([1, 2], 2),
        ]
        for elts, expected in cases:
            linked_list = LinkedList(*elts)
            self.assertEqual(linked_list.size(), expected,
                             msg=f'{expected=}')
    def test_equality(self):
        cases = [
            ([], [], True),
            ([1], [], False),
            ([1], [1], True),
            ([1], [1, 2], False),
        ]
        for xs, ys, expected in cases:
            x = LinkedList(*xs)
            y = LinkedList(*ys)
            self.assertEqual(x == y, expected,
                             msg=f'{x=} {y=}')
    def test_lookup(self):
        cases = [
            ([], None, lambda exp: exp is None),
            ([None], None, lambda exp: exp.elt is None),
            ([], 0, lambda exp: exp is None),
            ([], 1, lambda exp: exp is None),
            ([1], 1, lambda exp: exp.elt == 1),
            ([1, 2], 2, lambda exp: exp.elt == 2),
            ([1, 2], 3, lambda exp: exp is None),
        ]
        for elts, key, expected_func in cases:
            linked_list = LinkedList(*elts)
            self.assertTrue(expected_func(linked_list.lookup(key)),
                             msg=f'{key=}')
    def test_deletion_basic(self):
        linked_list = LinkedList(1, 2, 3)
        # If we delete element 1, we're gonna be pointing at 2, then 3.
        linked_list.delete_after()
        self.assertEqual(linked_list, LinkedList(2, 3))

    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=1,
                    max_size=20))
    def test_deletion_random(self, given_elts: list[int]):
        linked_list = LinkedList(*given_elts)
        deletions = random.randint(0, len(given_elts))
        for _ in range(deletions):
            linked_list.delete_after()
        self.assertEqual(linked_list.size(), len(given_elts) - deletions)

    def test_deletion_nop(self):
        linked_list = LinkedList()
        linked_list.delete_after()
        self.assertEqual(linked_list.size(), 0)

if __name__ == "__main__":
    unittest.main(exit=False)
