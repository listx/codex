from __future__ import annotations
from typing import Any, Callable, Optional
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
