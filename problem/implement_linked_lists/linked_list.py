from __future__ import annotations
from typing import Any, Optional
class LinkedList:
    def __init__(self, *args):
        self.elt = None
        self.next = None
        for elt in reversed(args):
            self.insert(elt)
    def insert(self, elt: Any) -> None:  #ref:insert
        node_new = LinkedList()
        node_new.elt = elt
        node_new.next = self.next
        self.next = node_new
    def __repr__(self):
        elts = []
        node = self
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        return "%s.%s(%s)" % (self.__class__.__module__,
                            self.__class__.__qualname__,
                            ", ".join(elts))
    def size(self) -> int:
        # Skip head node which doesn't hold any element.
        node = self.next
    
        n = 0
        while node:
            n += 1
            node = node.next
    
        return n
    def equal(self, b: LinkedList) -> bool:
        a = self
        while a.next or b.next:
            if a.next and b.next and a.next.elt == b.next.elt:
                a = a.next
                b = b.next
                continue
            return False
        return True
    def lookup(self, elt: Any) -> Optional[LinkedList]:
    
        current_node = self.next
    
        while current_node and current_node.elt != elt:
            current_node = current_node.next
    
        # This will be None if we failed to find the given element.
        return current_node
    def delete_after(self) -> None:
        if self.next is None:
            return
    
        self.next = self.next.next
