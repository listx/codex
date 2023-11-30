from binary_tree.binary_tree import BinaryTree, Node
import binary_search_tree.binary_search_tree as BST
import collections
from hypothesis import given, strategies as st
from typing import List, NamedTuple, Optional
import unittest

def is_sorted(lst: List[int]) -> bool:
    return all(a <= b for a, b in zip(lst, lst[1:]))

def dfs_inorder(t: BinaryTree) -> bool:
    traversal_history = []
    def record(x: Node):
        traversal_history.append(x.val)
    t.traverse_inorder(record)

    return is_sorted(traversal_history)
def dfs_inorder_manual(t: BinaryTree) -> bool:
    if t.root is None:
        return True

    last = None
    def helper(x: Optional[Node]) -> bool:
        nonlocal last

        if x is None:
            return True

        if not helper(x.left):
            return False

        if last is not None and last > x.val:
            return False
        last = x.val

        if not helper(x.right):
            return False

        return True

    return helper(t.root)
def dfs_preorder_range(t: BinaryTree) -> bool:
    def helper(x: Optional[Node], lo=None, hi=None) -> bool:
        if x is None:
            return True

        # Root node. Check children directly, because our starting ranges lo and
        # hi are both None (rendering our checks useless).
        if not lo and not hi:
            if x.left and not x.left.val < x.val:
                return False
            if x.right and not x.val < x.right.val:
                return False

        # Non-root node.
        if lo and not lo < x.val:
            return False
        if hi and not x.val < hi:
            return False
        return (helper(x.left, lo, x.val) and
                helper(x.right, x.val, hi))

    return helper(t.root)
def bfs(t: BinaryTree) -> bool:

    class QueueEntry(NamedTuple):
        node: Optional[Node]
        lo: float
        hi: float

    q = collections.deque([QueueEntry(t.root, float("-inf"), float("inf"))])

    while q:
        x, lo, hi = q.popleft()

        if x:
            if not lo < x.val < hi:
                return False

            q.append(QueueEntry(x.left, lo, x.val))
            q.append(QueueEntry(x.right, x.val, hi))

    return True

# Utility function for property-based tests.
# Convert BST into a binary tree. Of the "key" and "val" of each BST node, we
# only preserve the "key".
def convert_keys_to_bt(bst: BST.BinarySearchTree) -> BinaryTree:
    bt = BinaryTree()

    if bst.root is None:
        return bt

    bt.root = Node()

    def helper(x: Optional[BST.Node], cursor: Optional[Node]):
        if x is None:
            return
        if cursor is None:
            return

        # A binary tree node's value is actually the "key" of the BST.
        cursor.val = x.key

        if x.left is not None:
            cursor.left = Node()
            helper(x.left, cursor.left)

        if x.right is not None:
            cursor.right = Node()
            helper(x.right, cursor.right)

    helper(bst.root, bt.root)

    return bt

class Test(unittest.TestCase):
    def test_basic(self):
        # Empty tree is a valid BST.
        t = BinaryTree()
        result = dfs_inorder(t)
        self.assertEqual(result, True)

        # Basic happy case.
        t = BinaryTree()
        t.insert(50, [])
        t.insert(25, [0])
        t.insert(75, [1])
        result = dfs_inorder(t)
        self.assertEqual(result, True)

        # Basic unhappy cases.
        t = BinaryTree()
        t.insert(1, [])
        t.insert(0, [1])
        result = dfs_inorder(t)
        self.assertEqual(result, False)
        t = BinaryTree()
        t.insert(100, [])
        t.insert(25, [0])
        t.insert(75, [1])
        result = dfs_inorder(t)
        self.assertEqual(result, False)
    @given(st.lists(st.integers(min_value=1, max_value=50),
                    min_size=1,
                    max_size=50))
    def test_converter(self, keys: List[int]):
        bst = BST.BinarySearchTree()
        for key in keys:
            bst.insert(key)

        traversal_history_bst = []
        def record_traversal_history_bst(x: BST.Node):
            traversal_history_bst.append(x.key)
        bst.traverse_preorder(record_traversal_history_bst)

        bt = convert_keys_to_bt(bst)

        traversal_history_bt = []
        def record_traversal_history_bt(x: Node):
            traversal_history_bt.append(x.val)
        bt.traverse_preorder(record_traversal_history_bt)

        self.assertEqual(traversal_history_bt, traversal_history_bst)
    @given(st.lists(st.integers(min_value=1, max_value=50),
                    min_size=1,
                    max_size=50))
    def test_random_BSTs_are_all_valid_BSTs(self, keys: List[int]):
        bst = BST.BinarySearchTree()
        for key in keys:
            bst.insert(key)

        bt = convert_keys_to_bt(bst)

        self.assertEqual(True, dfs_inorder(bt))
        self.assertEqual(True, dfs_inorder_manual(bt))
        self.assertEqual(True, dfs_preorder_range(bt))
        self.assertEqual(True, bfs(bt))
    @given(st.lists(st.integers(min_value=1, max_value=50),
                    min_size=2, # The root must have at least 1 child.
                    max_size=50,
                    unique=True),
           st.randoms())
    def test_invalid_BSTs(self, keys: List[int], rand):
        bst = BST.BinarySearchTree()
        for key in keys:
            bst.insert(key)

        bt = convert_keys_to_bt(bst)

        # Pick a random index. This index will be used to pick a node in the binary
        # tree at random, to assign a BST-property-breaking value. Because our BST
        # keys are in the range 1 to 50, we choose 0 and 51 as the special
        # BST-property-breaking values.
        chosen_idx = rand.randint(0, bst.size() - 1)

        bad_lo = 0
        bad_hi = 51
        seen_idx = 0
        stop = False

        # direction_hist is a 2-bit number, the first bit meaning "I went left", and
        # the second bit meaning "I went right". We use this to check the overall
        # history of which child nodes we've followed to reach the current node
        # under consideration.
        def mutate(x: Optional[Node], direction_hist: int):
            nonlocal seen_idx
            nonlocal stop

            if not x:
                return

            if stop:
                return

            if seen_idx == chosen_idx:
                # Our mutate() function depends on direction_hist, but for the root
                # node this will always be empty. Sometimes the root node may only
                # have one child, instead of two (as basic BSTs are not
                # self-balancing). So if we chose the root node to mutate, take care
                # to check if we only have one child, and choose the bad value
                # accordingly.
                if chosen_idx == 0:
                    if x.left is None:
                        x.val = bad_hi
                    else:
                        x.val = bad_lo
                else:
                    # Non-root node.

                    # We only went left so far. There is a chance that we're at the
                    # leftmost child node. In all other cases setting a min value (0)
                    # would work to break this tree's BST property, but not for this
                    # leftmost leaf node. So assign the opposite (just beyond max)
                    # value.
                    if direction_hist == 1:
                        x.val = bad_hi
                    # If we've visited both left and child nodes so far, then we can
                    # assign either bad_lo or bad_hi --- it doesn't matter. This
                    # else-condition also covers the case where we only went right, so
                    # our hand is forced to choose bad_lo here.
                    else:
                        x.val = bad_lo

                # We've performed the mutation we wanted, so stop traversing the
                # tree.
                stop = True

            seen_idx += 1

            mutate(x.left, direction_hist | 1)
            mutate(x.right, direction_hist | 2)

        mutate(bt.root, 0)

        self.assertEqual(False, dfs_inorder(bt))
        self.assertEqual(False, dfs_inorder_manual(bt))
        self.assertEqual(False, dfs_preorder_range(bt))
        self.assertEqual(False, bfs(bt))

if __name__ == "__main__":
    unittest.main(exit=False)
