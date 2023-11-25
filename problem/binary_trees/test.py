from __future__ import annotations
from hypothesis import given, strategies as st
import unittest

from .binary_tree import BinaryTree, Node

class Test(unittest.TestCase):
    def test_init(self):
        # Initializing with no arguments results in a tree with no nodes.
        t = BinaryTree()
        self.assertEqual(t.root, None)
        self.assertEqual(t.size(), 0)

        # Initializing with "None" as an argument is basically the same thing.
        t = BinaryTree(None)
        self.assertEqual(t.root, None)
        self.assertEqual(t.size(), 0)

        # Initializing with an argument is allowed but we can only populate a single
        # BinaryTree (if we want to create more nodes, we have to use insert()).
        t = BinaryTree(1)
        self.assertEqual(t.root.val, 1)
        self.assertEqual(t.size(), 1)
    def test_insert(self):
        t = BinaryTree(1)
        self.assertEqual(t.size(), 1)
        t.insert(2, [0])
        self.assertEqual(t.size(), 2)
        t.insert(3, [1])
        self.assertEqual(t.size(), 3)
        t.insert(4, [0, 0])
        self.assertEqual(t.size(), 4)
        # Inserting at the same location does not update the count.
        t.insert(50, [0, 0])
        self.assertEqual(t.size(), 4)

        # Check sizes at every child node as well.
        self.assertEqual(t.root.left.count, 2)
        self.assertEqual(t.root.right.count, 1)
        self.assertEqual(t.root.left.left.count, 1)
    def test_lookup(self):
        t = BinaryTree(1)
        t.insert(2, [0])
        t.insert(3, [1])
        t.insert(4, [0, 0])
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.lookup([0, 0]), 4)
    def test_delete(self):
        t = BinaryTree()
        self.assertRaises(ValueError, t.lookup, [])
        self.assertEqual(t.size(), 0)

        t = self.make_complete_tree(3)
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 3)

        t = self.make_complete_tree(1)
        self.assertEqual(t.lookup([]), 1)
        deleted = t.delete()
        self.assertEqual(deleted, 1)
        self.assertRaises(ValueError, t.lookup, [])
        self.assertEqual(t.size(), 0)

        # Deleting the child of a leaf node is a NOP (there's nothing to delete).
        t = self.make_complete_tree(3)
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 3)
        deleted = t.delete(self.tree_path(1))
        self.assertEqual(deleted, 1)
        self.assertEqual(t.lookup([]), 2)
        self.assertRaises(ValueError, t.lookup, [0])
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 2)
        # Deleting the None object at [0] results in a NOP.
        self.assertEqual(self.tree_path(2), [0])
        t.delete(self.tree_path(2))
        self.assertEqual(t.size(), 2)

        t = self.make_complete_tree(3)
        self.assertEqual(t.size(), 3)
        t.delete([]) # Delete root node.
        self.assertEqual(t.lookup([]), 2)
        self.assertRaises(ValueError, t.lookup, [0])
        # 3 is 2's child now.
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 2)

        # Delete non-root, leaf node (no children).
        t = self.make_complete_tree(3)
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.size(), 3)
        self.assertEqual(t.root.val, 1)
        self.assertEqual(t.lookup([0]), 2)
        t.delete([0])
        self.assertRaises(ValueError, t.lookup, [0])
        self.assertEqual(t.size(), 2)
        self.assertEqual(t.lookup([1]), 3)
        t.delete([1])
        self.assertRaises(ValueError, t.lookup, [1])
        self.assertEqual(t.size(), 1)

        # Delete non-root node (1 child). We want to delete 2, when 4 is its child.
        t = self.make_complete_tree(4)
        self.assertEqual(t.size(), 4)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([0, 0]), 4)
        t.delete([0]) # Delete 2, making its only child 4 its successor.
        self.assertEqual(t.size(), 3)
        self.assertEqual(t.lookup([0]), 4)
        t.delete([0]) # Delete the successor.
        self.assertEqual(t.size(), 2)
        self.assertRaises(ValueError, t.lookup, [0])

        # Same as above, but the successor is the right child.
        t = self.make_complete_tree(6)
        self.assertEqual(t.size(), 6)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([0, 0]), 4)
        self.assertEqual(t.lookup([0, 1]), 5)
        t.delete([0, 0])
        # Delete 2, making its only child 5 its successor (this time its child on
        # the right side).
        t.delete([0])
        self.assertEqual(t.lookup([0]), 5)
        self.assertEqual(t.size(), 4)

        # Delete non-root node which has 2 children. Expect its leftmost leaf node
        # to be its successor.
        t = self.make_complete_tree(8)
        self.assertEqual(t.size(), 8)
        # Delete 2. This makes 8 the leftmost leaf node, making it its successor.
        t.delete([0])
        self.assertEqual(t.lookup([0]), 8)
        self.assertEqual(t.size(), 7)
        # The other nodes are untouched.
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.lookup([0, 0]), 4)
        self.assertEqual(t.lookup([0, 1]), 5)
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.lookup([1, 0]), 6)
        self.assertEqual(t.lookup([1, 1]), 7)

        # Successor node is several levels down the tree.
        t = BinaryTree(10)
        t.insert(3, [1])
        t.insert(8, [1, 0])
        t.insert(9, [1, 0, 1])
        t.insert(30, [1, 0, 1, 0]) # Successor (quite far down).
        t.insert(17, [1, 1])
        t.insert(15, [1, 1, 1])
        t.insert(55, [1, 1, 1, 0])
        self.assertEqual(t.size(), 8)
        t.delete([1])
        self.assertEqual(t.size(), 7)
        self.assertEqual(t.lookup([1]), 30) # 30 is the successor.
        self.assertEqual(t.lookup([1, 1]), 17)
        self.assertEqual(t.lookup([1, 1, 1]), 15)
        self.assertEqual(t.lookup([1, 1, 1, 0]), 55)
        self.assertEqual(t.lookup([1, 0]), 8)
        self.assertEqual(t.lookup([1, 0, 1]), 9)
        self.assertRaises(ValueError, t.lookup, [1, 0, 1, 0])
        self.assertRaises(ValueError, t.lookup, [1, 0, 1, 1])
    def test_traversal(self):
        traversal_history = []
        def record_traversal_history(x: Node):
            traversal_history.append(x.val)

        t = BinaryTree()
        t.insert(5, [])
        t.insert(1, [0])
        t.insert(9, [1])
        t.insert(0, [0, 0])
        t.insert(4, [0, 1])
        t.insert(2, [0, 1, 0])
        t.insert(7, [1, 0])
        t.insert(10, [1, 1])

        t.traverse_preorder(record_traversal_history)
        self.assertEqual(traversal_history, [5, 1, 0, 4, 2, 9, 7, 10])

        traversal_history = []
        t.traverse_inorder(record_traversal_history)
        self.assertEqual(traversal_history, [0, 1, 2, 4, 5, 7, 9, 10])

        traversal_history = []
        t.traverse_postorder(record_traversal_history)
        self.assertEqual(traversal_history, [0, 2, 4, 1, 7, 10, 9, 5])

        traversal_history = []
        t.bfs(record_traversal_history)
        self.assertEqual(traversal_history, [5, 1, 9, 0, 4, 7, 10, 2])

        traversal_history = []
        t.bfs_single_pass(record_traversal_history)
        self.assertEqual(traversal_history, [5, 1, 9, 0, 4, 7, 10, 2])
    # Helper function to create complete trees of a given size.
    def make_complete_tree(self, size: int):
        t = BinaryTree()
        for n in range(1, size + 1):
            t.insert(n, self.tree_path(n))
        return t

    # Convert a number into into binary form, but as a list of binary digits
    # (instead of a string).
    def bin_digits(self, n: int) -> list[int]:
        return [int(c) for c in str(bin(n))[2:]]

    # Return a path like "[1, 0, 1, ...]" for a node name in a perfect tree.
    def tree_path(self, n: int):
        # 1 is the root node.
        if n <= 1:
            n = 1
        return self.bin_digits(n)[1:]
    @given(st.integers(min_value=1, max_value=30))
    def test_delete_random_at_root(self, deletions: int):
        starting_size = 31
        t = self.make_complete_tree(starting_size)
        # Repeatedly delete from the root node.
        for _ in range(deletions):
            t.delete([])
        self.assertEqual(t.size(), starting_size - deletions)
    @given(st.lists(st.integers(min_value=0, max_value=15),
                    min_size=0,
                    max_size=15))
    def test_delete_random_at_random(self, deletion_paths: list[int]):
        starting_size = 15
        t = self.make_complete_tree(starting_size)
        self.assertEqual(t.size(), 15)

        # Repeatedly delete from a random node in the tree.
        deleted_count = 0
        for deletion_path in deletion_paths:
            path = self.tree_path(deletion_path)
            deleted_node = t.delete(path)
            # Only count the deletion if we actually deleted a node (maybe the path
            # was pointing to nothing).
            if deleted_node is not None:
                deleted_count += 1
        self.assertEqual(t.size(), starting_size - deleted_count)

if __name__ == "__main__":
    unittest.main(exit=False)
