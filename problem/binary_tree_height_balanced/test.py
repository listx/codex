from __future__ import annotations
from hypothesis import given, strategies as st
from typing import Optional, NamedTuple
import unittest

from binary_tree.binary_tree import BinaryTree, Node

def height(x: Optional[Node]) -> int:
    if x is None:
        return -1

    height_l = height(x.left)
    height_r = height(x.right)

    return max(height_l, height_r) + 1
def is_height_balanced__brute_force(x: Optional[Node]) -> bool:
    # If there is no node, then just consider it height-balanced. This also
    # matters when we recurse --- we are bound to run into a None object (when
    # looking at the children of leaf nodes), and we don't want to abort the
    # traversal as soon as we encounter them. So we are forced to return True.
    if x is None:
        return True

    # Traverse into the other nodes, making sure that we call the body of this
    # function exactly once for every Node.
    if not is_height_balanced__brute_force(x.left):
        return False
    if not is_height_balanced__brute_force(x.right):
        return False

    # "Visit" this node by doing the actual subtree height check for the left
    # and right children.
    height_l = height(x.left)
    height_r = height(x.right)

    big = max(height_l, height_r)
    small = min(height_l, height_r)
    delta = big - small

    return delta <= 1
def is_height_balanced__brute_force_preorder(x: Optional[Node]) -> bool:
    if x is None:
        return True

    height_l = height(x.left)
    height_r = height(x.right)

    big = max(height_l, height_r)
    small = min(height_l, height_r)
    delta = big - small

    if delta > 1:
        return False

    if not is_height_balanced__brute_force(x.left):
        return False
    if not is_height_balanced__brute_force(x.right):
        return False

    return True

def is_height_balanced__brute_force_inorder(x: Optional[Node]) -> bool:
    if x is None:
        return True

    if not is_height_balanced__brute_force(x.left):
        return False

    height_l = height(x.left)
    height_r = height(x.right)

    big = max(height_l, height_r)
    small = min(height_l, height_r)
    delta = big - small

    if delta > 1:
        return False

    if not is_height_balanced__brute_force(x.right):
        return False

    return True
class NodeInfo(NamedTuple):
    balanced: bool
    height: int
def get_balanced_status(x: Optional[Node]) -> NodeInfo:
    # Base case for recursion, just like for the brute force approach.
    if x is None:
        return NodeInfo(True, -1)

    # Early return if either the left or right subtrees were not balanced.
    ni_left = get_balanced_status(x.left)
    if not ni_left.balanced:
        return ni_left

    ni_right = get_balanced_status(x.right)
    if not ni_right.balanced:
        return ni_right

    # Both the left and right subtrees are balanced. But it could be that
    # the tree rooted at the current node is not balanced.
    big = max(ni_left.height, ni_right.height)
    small = min(ni_left.height, ni_right.height)
    delta = big - small

    if delta > 1:
        return NodeInfo(False, -1)

    # Current tree is balanced. The height of the tree is the maximum of the
    # heights of either subtree, plus 1.
    return NodeInfo(True, max(ni_left.height, ni_right.height) + 1)
def is_height_balanced__optimal(x: Optional[Node]) -> bool:
    return get_balanced_status(x).balanced

class Test(unittest.TestCase):
    def test_height(self):
        t = BinaryTree()
        self.assertEqual(height(t.root), -1)

        t = BinaryTree()
        t.insert(0, [])
        self.assertEqual(height(t.root), 0)

        t = BinaryTree()
        t.insert(0, [0, 0, 0])
        self.assertEqual(height(t.root), 3)
        self.assertEqual(height(t.root.left), 2)
        self.assertEqual(height(t.root.left.left), 1)
        self.assertEqual(height(t.root.left.left.left), 0)
        self.assertEqual(height(t.root.left.left.left.left), -1)

        t = BinaryTree()
        t.insert(0, [0, 0, 0])
        t.insert(0, [1, 1, 1])
        self.assertEqual(height(t.root), 3)

        t = BinaryTree()
        t.insert(0, [0])
        t.insert(0, [1, 1, 1])
        self.assertEqual(height(t.root), 3)

    def test_is_height_balanced(self):
        t = BinaryTree()
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        t = BinaryTree()
        t.insert(0, [])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        t = BinaryTree()
        t.insert(0, [])
        t.insert(0, [0])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        t = BinaryTree()
        t.insert(0, [])
        t.insert(0, [0])
        t.insert(0, [1])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        t = BinaryTree()
        t.insert(0, [])
        t.insert(0, [0, 0])
        t.insert(0, [1])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        t = BinaryTree()
        t.insert(0, [])
        t.insert(0, [0, 0])
        t.insert(0, [1, 1])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

        # Trivial unbalanced example.
        t = BinaryTree()
        t.insert(0, [])
        t.insert(0, [0, 0, 0])
        t.insert(0, [1])
        self.assertEqual(is_height_balanced__brute_force(t.root), False)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), False)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), False)
        self.assertEqual(is_height_balanced__optimal(t.root), False)

        # Elaborate balanced example (same as in the diagram in Figure 1).
        t = BinaryTree()
        t.insert(1, [])
        t.insert(2, [0])
        t.insert(3, [0, 0])
        t.insert(8, [0, 1])
        t.insert(9, [0, 1, 0])
        t.insert(10, [0, 1, 1])
        t.insert(4, [0, 0, 0])
        t.insert(7, [0, 0, 1])
        t.insert(5, [0, 0, 0, 0])
        t.insert(6, [0, 0, 0, 1])
        t.insert(11, [1])
        t.insert(12, [1, 0])
        t.insert(13, [1, 0, 0])
        t.insert(14, [1, 0, 1])
        t.insert(15, [1, 1])
        self.assertEqual(is_height_balanced__brute_force(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_preorder(t.root), True)
        self.assertEqual(is_height_balanced__brute_force_inorder(t.root), True)
        self.assertEqual(is_height_balanced__optimal(t.root), True)

    # Populate a random binary tree. Check that the optimal solution agrees with
    # the brute force approach.
    @given(st.lists(st.lists(st.integers(min_value=0, max_value=1),
                            min_size=0,
                            max_size=32),
                    min_size=0,
                    max_size=32))
    def test_is_height_balanced__random(self, paths: list[list[int]]):
        t = BinaryTree()
        for path in paths:
            t.insert(0, path)

        bf = is_height_balanced__brute_force(t.root)
        bf_pre = is_height_balanced__brute_force_preorder(t.root)
        bf_in = is_height_balanced__brute_force_inorder(t.root)
        o = is_height_balanced__optimal(t.root)

        self.assertEqual(bf, bf_pre)
        self.assertEqual(bf, bf_in)
        self.assertEqual(bf, o)

if __name__ == "__main__":
    unittest.main(exit=False)
