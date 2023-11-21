from __future__ import annotations
from hypothesis import given, strategies as st
import unittest
from typing import Any, Callable, Optional

# BEGIN binary tree implementation.
from collections import deque

class Node:
    def __init__(self, key: int, val: Any=None):
        self.key = key
        self.val = val
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.count = 1
class BinarySearchTree:
    def __init__(self, root: Optional[Node]=None):
        self.root = root
    def insert(self, key: int, val: Any=None):
        self.root = self._insert(self.root, key, val)

    def _insert(self, x: Optional[Node], key: int, val: Any=None):
        if x is None:
            return Node(key, val)
        if key < x.key:
            x.left = self._insert(x.left, key, val)
        elif key > x.key:
            x.right = self._insert(x.right, key, val)
        else:
            x.val = val
        x.count = self._size(x.left) + self._size(x.right) + 1
        return x
    def insert_int(self, *args: int):
        for i, arg in enumerate(args):
            self.root = self._insert(self.root, arg, f"val={arg}")
    def size(self):
        return self._size(self.root)
    def _size(self, x: Optional[Node]):
        if x is None:
            return 0
        return x.count
    def lookup(self, key: int):
        return self._lookup(self.root, key)

    def _lookup(self, x: Optional[Node], key: int):
        if x is None:
            return None
        if key < x.key:
            return self._lookup(x.left, key)
        elif key > x.key:
            return self._lookup(x.right, key)
        else:
            return x.val
    def delete(self, key: int):
        self.root = self._delete(self.root, key)
    def _delete(self, x: Optional[Node], key: int):
        # If there is no node to delete (because we could not find the node we
        # wanted to delete), then deletion is a NOP.
        if x is None:
            return None
        # If the key doesn't match for the current node, keep searching.
        if key < x.key:
            x.left = self._delete(x.left, key)
        # Ditto.
        elif key > x.key:
            x.right = self._delete(x.right, key)
        # Found the node we want to delete.
        else:
            # If either the left or right child is None, return the other child. If
            # the other child is None, then this means that this node had no
            # children. If the other child is not None, this means this node only
            # had 1 child (which means we're done).
            if x.left is None:
                return x.right
            if x.right is None:
                return x.left

            # We have two children. We need to pick a replacement (smallest key
            # greater than the current key).

            # Save a link to the node to be deleted, because we want links to the
            # original children of x.
            y = x

            # Get the successor node with the lowest key greater than x.key.
            x = self._min(x.right)

            # We can't just do "x.right = y.right" because y.right contains x
            # (self._min(x.right) is a read operation). So delete the successor out
            # of the right subtree, and assign this pruned subtree to be the
            # successor's right child.
            x.right = self._delete_min(y.right)

            # The original left child of (the now-deleted) x is now the left child
            # of x's successor. We have to do this operation last because otherwise
            # this left child interferes with the algorithm in _delete_min().
            x.left = y.left

        x.count = self._size(x.left) + self._size(x.right) + 1

        return x

    def min(self) -> Optional[int]:
        if self.root is None:
            return None
        x = self._min(self.root)
        if x is None:
            return None
        return x.key

    # Find the node with the smallest key in the given tree, rooted at node x.
    def _min(self, x: Node) -> Node:
        while True:
            # If we have nothing smaller than x, this is the minimum.
            if x.left is None:
                break
            x = x.left
        return x

    def delete_min(self):
        self.root = self._delete_min(self.root)

    # Return a tree rooted at node x, but with the node containing the smallest key
    # in it removed from this tree.
    def _delete_min(self, x: Optional[Node]) -> Optional[Node]:
        if x is None:
            return None
        if x.left is None:
            return x.right
        x.left = self._delete_min(x.left)
        x.count = self._size(x.left) + self._size(x.right) + 1
        return x
    def traverse_preorder(self, func: Callable[[Node], None]):
        return self._traverse_preorder(self.root, func)

    def _traverse_preorder(self, x: Optional[Node], func: Callable[[Node], None]):
        if x is None:
            return
        func(x)
        self._traverse_preorder(x.left, func)
        self._traverse_preorder(x.right, func)

    def traverse_inorder(self, func: Callable[[Node], None]):
        return self._traverse_inorder(self.root, func)

    def _traverse_inorder(self, x: Optional[Node], func: Callable[[Node], None]):
        if x is None:
            return
        self._traverse_inorder(x.left, func)
        func(x)
        self._traverse_inorder(x.right, func)

    def traverse_postorder(self, func: Callable[[Node], None]):
        return self._traverse_postorder(self.root, func)

    def _traverse_postorder(self, x: Optional[Node], func: Callable[[Node], None]):
        if x is None:
            return
        self._traverse_postorder(x.left, func)
        self._traverse_postorder(x.right, func)
        func(x)
    def bfs(self, func: Callable[[Node], None]):
        return self._bfs(self.root, func)

    def _bfs(self, x: Optional[Node], func: Callable[[Node], None]):
        if x is None:
            return

        nodes_at_current_depth = [x]
        while nodes_at_current_depth:
            # Process all nodes at current depth.
            for node in nodes_at_current_depth:
                func(node)

            # Now add all nodes at the next depth.
            children = []
            for node in nodes_at_current_depth:
                if not node:
                    continue
                if node.left:
                    children.append(node.left)
                if node.right:
                    children.append(node.right)

            # Repeat the loop at the next depth.
            nodes_at_current_depth = children
    def bfs_single_pass(self, func: Callable[[Node], None]):
        return self._bfs(self.root, func)

    def _bfs_single_pass(self, x: Optional[Node], func: Callable[[Node], None]):
        if x is None:
            return

        q = deque([x])
        while q:
            # Process the head of the queue. As we process each one, just before we
            # discard it we check if it has children, and if so, add them to the end
            # of the queue.

            node = q.popleft()
            if not node:
                continue

            func(node)

            # Add this node's children, if any.
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
# END binary tree implementation.

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
