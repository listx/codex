from __future__ import annotations
from typing import Any, Callable, Optional, List
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
