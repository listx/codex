#from binary_tree.binary_tree import BinaryTree, Node
#import binary_search_tree.binary_search_tree as BST
#import collections
#from hypothesis import given, strategies as st
from typing import List, NamedTuple
import unittest

def recursive(discs_to_move: int):
    result = []

    def record_steps(discs: int,
                     rod_start: str,
                     rod_final: str,
                     rod_other: str):

        if not discs:
            return

        # Move subtower from the starting rod to the other rod. "First leg" of
        # recursion.
        record_steps(discs - 1, rod_start, rod_other, rod_final)

        # Move largest disc to final rod, and record this step. We reuse "discs"
        # as the disc "id". "Largest" here depends on context.
        result.append(str(discs) + rod_start + rod_final)

        # Move subtower from the other rod to the final rod. "Second leg" of
        # recursion.
        record_steps(discs - 1, rod_other, rod_final, rod_start)

    # Record the steps!
    record_steps(discs_to_move, 'A', 'B', 'C')

    return result
def iterative(discs_to_move: int):

    result = []

    def record_steps(discs: int,
                     rod_start: str,
                     rod_final: str,
                     rod_other: str):

        class RecursiveCall(NamedTuple):
            discs: int
            rod_start: str
            rod_final: str
            rod_other: str

        callstack: List[RecursiveCall] = []

        while discs or callstack:

            # Simulate a recursive call. Initially, this loop simulates the
            # "first leg" of recursion. Later, it will simulate the second leg
            # as well.
            while discs:
                rc = RecursiveCall(
                    discs,
                    rod_start,
                    rod_final,
                    rod_other,
                )
                callstack.append(rc)
                rod_final, rod_other = rod_other, rod_final
                discs -= 1

            # "Execute" the function call at the top of the stack. We don't
            # really care how the function call got to the top --- we just
            # execute it to make our "CPU" make progress.
            exec_me = callstack.pop()
            result.append(str(exec_me.discs) +
                          exec_me.rod_start +
                          exec_me.rod_final)

            # The combination of this stanza and the above while loop just above
            # will simulate the second leg of recursion. Recurse
            if exec_me.discs > 0:
                discs = exec_me.discs - 1
                rod_start = exec_me.rod_other
                rod_final = exec_me.rod_final
                rod_other = exec_me.rod_start

    record_steps(discs_to_move, 'A', 'B', 'C')

    return result

class Test(unittest.TestCase):
    def test_recursive(self):
        self.assertEqual(recursive(0), [])
        self.assertEqual(recursive(1), ["1AB"])
        self.assertEqual(recursive(2), ["1AC", "2AB", "1CB"])
        self.assertEqual(recursive(3), ["1AB", "2AC", "1BC",
                                        "3AB",
                                        "1CA", "2CB", "1AB"])
    def test_iterative(self):
        self.assertEqual(iterative(0), [])
        self.assertEqual(iterative(1), ["1AB"])
        self.assertEqual(iterative(2), ["1AC", "2AB", "1CB"])
        self.assertEqual(iterative(3), ["1AB", "2AC", "1BC",
                                        "3AB",
                                        "1CA", "2CB", "1AB"])

    # Do the recursive and iterative solutions agree with each other?
    def test_cross_check(self):
        for i in range(8):
            self.assertEqual(recursive(i), iterative(i))

if __name__ == "__main__":
    unittest.main(exit=False)
