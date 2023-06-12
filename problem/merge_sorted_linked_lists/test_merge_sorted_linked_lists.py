from hypothesis import given, strategies as st
import random
import unittest

import merge_sorted_linked_lists.linked_list as lib

def merge(a: lib.LinkedList, b: lib.LinkedList) -> lib.LinkedList:
    head = tail = lib.LinkedList()
    a = a.next
    b = b.next
    while a or b:
        if a and b:
            if a.elt < b.elt:
                tail.next = a
                a = a.next
            else:
                tail.next = b
                b = b.next
        else:
            tail.next = a or b
            break
        tail = tail.next
    return head

class Test(unittest.TestCase):
    def test_merge_simple_cases(self):
        cases = [
            ([], [], []),
            ([1], [], [1]),
            ([], [1], [1]),
            ([1], [1], [1, 1]),
            ([1, 2, 3], [1], [1, 1, 2, 3]),
            ([1, 2], [1, 3], [1, 1, 2, 3]),
            ([1, 3, 5], [2, 4, 6, 8, 10], [1, 2, 3, 4, 5, 6, 8, 10]),
            ([1, 2, 3], [], [1, 2, 3]),
            ([], [1, 2, 3], [1, 2, 3]),
        ]
        for list_a, list_b, list_expected in cases:
            a = lib.LinkedList(*list_a)
            b = lib.LinkedList(*list_b)
            expected = lib.LinkedList(*list_expected)

            got = merge(a, b)
            self.assertTrue(got.equal(expected),
                            msg=f'{got=} {list_expected=}')

    @given(st.lists(st.integers(min_value=1, max_value=100),
                    min_size=0,
                    max_size=20))
    def test_merge_random(self, given_elts: list[int]):
        size_a = random.randint(0, len(given_elts))
        a = given_elts[0:size_a]
        b = given_elts[size_a:]
        expected = lib.LinkedList(*sorted(given_elts))
        got = merge(lib.LinkedList(*sorted(a)),
                    lib.LinkedList(*sorted(b)))
        self.assertTrue(got.equal(expected),
                        msg=f'{got=} {expected=}')
if __name__ == "__main__":
    unittest.main(exit=False)
