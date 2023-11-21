from __future__ import annotations
from hypothesis import given, strategies as st
import unittest
from typing import Any, Optional
import random

class LinkedList:
    def __init__(self, *args):
        self.elt = None
        self.next = None
        for elt in reversed(args):
            self.insert(elt)
    def insert(self, elt: Any) -> None:  #ref:insert
        node_new = LinkedList()
        node_new.elt = elt
        node_new.next = self.next
        self.next = node_new
    def __repr__(self):
        elts = []
        node = self
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        return "%s.%s(%s)" % (self.__class__.__module__,
                            self.__class__.__qualname__,
                            ", ".join(elts))
    def size(self) -> int:
        # Skip head node which doesn't hold any element.
        node = self.next

        n = 0
        while node:
            n += 1
            node = node.next

        return n
    def __eq__(self, b) -> bool:
        if not isinstance(b, LinkedList):
            return NotImplemented
        a = self
        while a.next or b.next:
            if a.next and b.next and a.next.elt == b.next.elt:
                a = a.next
                b = b.next
                continue
            return False
        return True
    def lookup(self, elt: Any) -> Optional[LinkedList]:

        current_node = self.next

        while current_node and current_node.elt != elt:
            current_node = current_node.next

        # This will be None if we failed to find the given element.
        return current_node
    def delete_after(self) -> None:
        if self.next is None:
            return

        self.next = self.next.next

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
