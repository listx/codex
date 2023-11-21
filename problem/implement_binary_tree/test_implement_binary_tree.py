from __future__ import annotations
from hypothesis import given, strategies as st
import unittest
from typing import Any, Callable, Optional, List

# BEGIN binary tree implementation.
from collections import deque

class Node:
    def __init__(self, val: Any=None):
        self.val = val
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.count = 1
class BinaryTree:
    def __init__(self, val: Any=None):
        if val is None:
            self.root = None
        else:
            self.root = Node(val)
    def insert(self, val: Any, directions: List[int]):
        self.root = self._insert(self.root, val, directions)
    def _insert(self, x: Optional[Node], val: Any, directions: List[int]):
        if x is None:
            x = Node()
        start = x
        hist = deque([(x, False)])
        for direction in directions:
            new_node = False
            if direction:
                if x.right is None:
                    x.right = Node()
                    new_node = True
                x = x.right
            else:
                if x.left is None:
                    x.left = Node()
                    new_node = True
                x = x.left
            hist.append((x, new_node))

        # Update counts back up the tree (by visiting seen nodes) by processing
        # hist. We skip the last node because it already has a count of 1 by
        # default.
        delta = 0
        while hist:
            node, new_node = hist.pop()
            if new_node:
                delta += 1
                if delta == 1:
                    continue
            node.count += delta

        # Finally, set the value on the node.
        x.val = val
        return start
    def size(self):
        return self._size(self.root)
    def _size(self, x: Optional[Node]):
        if x is None:
            return 0
        return x.count
    def lookup(self, directions: List[int]):
        return self._lookup(self.root, directions)
    def _lookup(self, x: Optional[Node], directions: List[int]):
        if x is None:
            raise ValueError("no root node to start navigation from")
        for direction in directions:
            if x is None:
                raise ValueError("could not navigate to node")
            if direction:
                x = x.right
            else:
                x = x.left
        if x is None:
            raise ValueError("navigated to a None type, not a node")
        return x.val
    def _delete(self, x: Optional[Node], directions: List[int]) -> Optional[Node]:
        # If the starting node is not a node, we cannot do any navigation on it to
        # find the node we want to delete. Abort.
        if x is None:
            return None

        # Find the node to delete. We recurse down here, but the main point is that
        # only the last call to _delete() will do the actual deletion. All calls to
        # _delete() leading up to the last one just perform navigation and
        # assignment back up the hierarchy.
        if directions:
            if directions[0]:
                x.right = self._delete(x.right, directions[1:])
            else:
                x.left = self._delete(x.left, directions[1:])
            x.count = self._size(x.left) + self._size(x.right) + 1
            return x

        # We've arrived at the node we want to delete. We deal with the 3 possible
        # cases.

        # If there are two children, we have to pick a replacement from the
        # leftmost root node. Picking a replacement is a bit tricky because the
        # current parent of the replacement needs to no longer point to it
        # (otherwise we'll end up just duplicating the replacement).
        if x.left is not None and x.right is not None:
            y = x
            # Overwrite x, "deleting" it by replacing it with its leftmost leaf
            # node. But make this leaf node a non-leaf node by making it point to
            # x's children (saved in y).
            x = self._pop_leftmost_leaf_node(x.left)
            # Only assign the previous left child as the replacement's left child if
            # the replacement is not itself the left child. I.e., avoid a possible
            # cycle.
            if x != y.left:
                x.left = y.left
            x.right = y.right
            # We have 1 less node than before. We can't use x.count because x is the
            # leaf node (and its count is 1).
            x.count = y.count - 1
        # If there is just one child, then make that one the replacement.
        elif x.left is not None:
            x = x.left
        elif x.right is not None:
            x = x.right
        # No children. Easy case where we just assign None to self (we are
        # deleting this BinaryTree object, essentially).
        else:
            return None

        return x
    def _pop_leftmost_leaf_node(self, x: Node) -> Node:
        hist = []
        went_left = False
        while True:
            if x.left is not None:
                hist.append(x)
                x = x.left
                went_left = True
                continue
            if x.right is not None:
                hist.append(x)
                x = x.right
                went_left = False
                continue
            break

        # If we had any children (descended down the tree), we have to modify it so
        # that the parent of the leaf node is no longer pointing to this leaf node.
        # Otherwise, the leaf node would still stay in the tree and would not be
        # "popped" out of it.
        if hist:
            if went_left:
                hist[-1].left = None
            else:
                hist[-1].right = None
        for h in hist:
            h.count -= 1

        return x
    def delete(self, directions: Optional[List[int]]=None):
        if directions is None:
            directions = []
        to_delete = None

        try:
            to_delete = self.lookup(directions)
        except ValueError:
            # The directions are either bogus, or at best point us to a None (not a
            # node). In both cases there is nothing more to do.
            return None
        else:
            self.root = self._delete(self.root, directions)
            # Return the node we wanted to delete. Because the operation above
            # completed successfully, it is guaranteed to have deleted it from the
            # tree (removed any link to this object from the tree, such that this
            # node lies outside of the realm of the tree).
            return to_delete
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

        t = self.make_perfect_tree(3)
        self.assertEqual(t.lookup([]), 1)
        self.assertEqual(t.lookup([0]), 2)
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 3)

        t = self.make_perfect_tree(1)
        self.assertEqual(t.lookup([]), 1)
        deleted = t.delete()
        self.assertEqual(deleted, 1)
        self.assertRaises(ValueError, t.lookup, [])
        self.assertEqual(t.size(), 0)

        # Deleting the child of a leaf node is a NOP (there's nothing to delete).
        t = self.make_perfect_tree(3)
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

        t = self.make_perfect_tree(3)
        self.assertEqual(t.size(), 3)
        t.delete([]) # Delete root node.
        self.assertEqual(t.lookup([]), 2)
        self.assertRaises(ValueError, t.lookup, [0])
        # 3 is 2's child now.
        self.assertEqual(t.lookup([1]), 3)
        self.assertEqual(t.size(), 2)

        # Delete non-root, leaf node (no children).
        t = self.make_perfect_tree(3)
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
        t = self.make_perfect_tree(4)
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
        t = self.make_perfect_tree(6)
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
        t = self.make_perfect_tree(8)
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
    # Helper function to create full trees of a given size.
    def make_perfect_tree(self, size: int):
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
        t = self.make_perfect_tree(starting_size)
        # Repeatedly delete from the root node.
        for _ in range(deletions):
            t.delete([])
        self.assertEqual(t.size(), starting_size - deletions)
    @given(st.lists(st.integers(min_value=0, max_value=15),
                    min_size=0,
                    max_size=15))
    def test_delete_random_at_random(self, deletion_paths: list[int]):
        starting_size = 15
        t = self.make_perfect_tree(starting_size)
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
