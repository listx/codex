from __future__ import annotations
from hypothesis import given, strategies as st
import unittest

from .binary_search_tree import BinarySearchTree, Node

class Test(unittest.TestCase):
    def test_init_empty(self):
        t = BinarySearchTree()
        self.assertEqual(0, t.size())

    def test_init_nonempty(self):
        root = Node(50, "a")
        t = BinarySearchTree(root)
        self.assertEqual(1, t.size())
    def test_insertion(self):
        t = BinarySearchTree()
        self.assertEqual(0, t.size())
        t.insert(50, "foo")
        self.assertEqual(1, t.size())
        # Inserting the same key (different value) results in the same size, because
        # the old node with the same key is replaced.
        t.insert(50, "bar")
        self.assertEqual(1, t.size())
        # Inserting a different key grows the tree by 1 node.
        t.insert_int(51)
        self.assertEqual(2, t.size())
        t.insert_int(52)
        self.assertEqual(3, t.size())
    def test_lookup(self):
        t = BinarySearchTree()
        self.assertEqual(t.lookup(5), None)
        t.insert_int(100)
        self.assertEqual(t.lookup(100), "val=100")
        # Manual insertion (bypassing insert_int()) allows us to set the value
        # directly.
        t.insert(100, "b")
        self.assertEqual(t.lookup(100), "b")
    def test_deletion(self):
        # Deletion on an empty tree is a NOP.
        t = BinarySearchTree()
        self.assertEqual(t.size(), 0)
        t.delete(5)
        self.assertEqual(t.size(), 0)

        # Delete the root node (no child).
        t = BinarySearchTree()
        t.insert_int(3)
        t.delete(3)
        self.assertEqual(t.size(), 0)

        # Delete the root node (successor is left child).
        t = BinarySearchTree()
        t.insert_int(3, 1)
        self.assertEqual(t.size(), 2)
        t.delete(3)
        self.assertEqual(t.size(), 1)
        self.assertEqual(t.root.val, "val=1")

        # Delete the root node (successor is right child).
        t = BinarySearchTree()
        t.insert_int(3, 4)
        self.assertEqual(t.size(), 2)
        t.delete(3)
        self.assertEqual(t.size(), 1)
        self.assertEqual(t.root.val, "val=4")

        # Delete the root node (has 2 children; replacement is successor of right
        # child, but the right child itself is the successor because it has no
        # children on the left).
        t = BinarySearchTree()
        t.insert_int(3, 4, 1, 5, 2)
        self.assertEqual(t.size(), 5)
        self.assertEqual(t.root.val, "val=3")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.left.right.val, "val=2")
        self.assertEqual(t.root.right.val, "val=4")
        self.assertEqual(t.root.right.right.val, "val=5")
        t.delete(3)
        self.assertEqual(t.size(), 4)
        self.assertEqual(t.root.val, "val=4")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.left.right.val, "val=2")
        self.assertEqual(t.root.right.val, "val=5")

        t = BinarySearchTree()
        t.insert_int(3, 5, 1, 4, 2, 6)
        self.assertEqual(t.size(), 6)
        self.assertEqual(t.root.val, "val=3")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.left.right.val, "val=2")
        self.assertEqual(t.root.right.val, "val=5")
        self.assertEqual(t.root.right.left.val, "val=4")
        self.assertEqual(t.root.right.right.val, "val=6")
        t.delete(5)
        self.assertEqual(t.size(), 5)
        self.assertEqual(t.root.val, "val=3")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.left.left, None)
        self.assertEqual(t.root.left.right.val, "val=2")
        self.assertEqual(t.root.right.val, "val=6")
        self.assertEqual(t.root.right.left.val, "val=4")
        self.assertEqual(t.root.right.right, None)

        t = BinarySearchTree()
        t.insert_int(2, 5, 7, 4, 3, 9, 1, 6)
        self.assertEqual(t.size(), 8)
        self.assertEqual(t.root.val, "val=2")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.right.val, "val=5")
        self.assertEqual(t.root.right.left.val, "val=4")
        self.assertEqual(t.root.right.left.left.val, "val=3")
        self.assertEqual(t.root.right.right.val, "val=7")
        self.assertEqual(t.root.right.right.left.val, "val=6")
        self.assertEqual(t.root.right.right.right.val, "val=9")
        t.delete(5)
        self.assertEqual(t.size(), 7)
        self.assertEqual(t.root.val, "val=2")
        self.assertEqual(t.root.left.val, "val=1")
        self.assertEqual(t.root.right.val, "val=6")
        self.assertEqual(t.root.right.left.val, "val=4")
        self.assertEqual(t.root.right.left.left.val, "val=3")
        self.assertEqual(t.root.right.right.val, "val=7")
        self.assertEqual(t.root.right.right.right.val, "val=9")
    @given(st.lists(st.integers(min_value=0, max_value=64),
                    min_size=0,
                    max_size=64),
           st.lists(st.integers(min_value=0, max_value=32),
                    min_size=0,
                    max_size=32))
    def test_delete_random_at_random(self, keys: list[int], to_delete: list[int]):
        keys_unique = list(dict.fromkeys(keys))
        to_delete_unique = list(dict.fromkeys(to_delete))
        starting_size = len(keys_unique)
        t = BinarySearchTree()
        t.insert_int(*keys)
        self.assertEqual(t.size(), starting_size)

        # Repeatedly delete from a random node in the tree.
        deleted_count = 0
        for delete_me in to_delete_unique:
            size_before = t.size()
            t.delete(delete_me)
            size_after = t.size()
            # Only count the deletion if we actually deleted a node. The presumption
            # here is that t.delete() only deletes a single node if it does delete
            # it (that it doesn't grow the tree, for example).
            if size_before != size_after:
                deleted_count += 1
        self.assertEqual(t.size(), starting_size - deleted_count)
    @given(st.lists(st.integers(min_value=0, max_value=32),
                    min_size=0,
                    max_size=32))
    def test_delete_random_tree_drain_all_keys(self, keys: list[int]):
        keys_unique = list(dict.fromkeys(keys))
        t = BinarySearchTree()
        t.insert_int(*keys)
        self.assertEqual(t.size(), len(keys_unique))

        for key in keys:
            t.delete(key)
        self.assertEqual(t.size(), 0)
    def test_traversal(self):
        traversal_history = []
        def record_traversal_history(x: Node):
            traversal_history.append(x.key)

        t = BinarySearchTree()
        t.insert_int(5, 1, 9, 4, 7, 2, 10, 0)

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
    @given(st.lists(st.integers(min_value=0, max_value=32),
                    min_size=0,
                    max_size=32))
    def test_delete_random_keys_are_always_sorted(self, keys: list[int]):
        t = BinarySearchTree()
        t.insert_int(*keys)

        traversal_history = []
        def record_traversal_history(x: Node):
            traversal_history.append(x.key)
        t.traverse_inorder(record_traversal_history)
        sorted_traversal_history = list(sorted(traversal_history))
        self.assertEqual(traversal_history, sorted_traversal_history)

if __name__ == "__main__":
    unittest.main(exit=False)
