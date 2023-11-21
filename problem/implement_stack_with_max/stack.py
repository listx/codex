from __future__ import annotations
from typing import Any, Optional
from implement_linked_list.linked_list import LinkedList

class StackNaive:
    def __init__(self, *args):
        self.ll = LinkedList()
        for elt in args:
            self.push(elt)
    def push(self, elt: Any) -> None:
        if self.size() == 0:
            self.ll.insert((elt, elt))
        else:
            self.ll.insert((elt, max(elt, self.max())))
    def max(self):
        if self.size() == 0:
            return None
        node = self.ll.next
        (_, max) = node.elt
        return max
    def pop(self) -> Optional[Any]:
        node = self.ll.next
        (elt, _) = node.elt if node else (None, None)
        self.ll.delete_after()
        return elt
    def __repr__(self):
        elts = []
        node = self.ll
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        return "%s.%s(%s)" % (self.__class__.__module__,
                            self.__class__.__qualname__,
                            ", ".join(elts))
    def size(self) -> int:
        return self.ll.size()
    def __eq__(self, other) -> bool:
        return self.ll == other.ll
class Stack(StackNaive):
    def __init__(self, *args):
        self.ll_max = LinkedList()
        super().__init__(*args)
    def push(self, elt: Any) -> None:
        self.ll.insert(elt)
        if self.size() == 1:
            self.ll_max.insert((elt, 1))
            return
        (max_cur, n) = self.ll_max.next.elt
        if elt == max_cur:
            self.ll_max.delete_after()
            self.ll_max.insert((max_cur, n+1))
        elif elt > max_cur:
            self.ll_max.insert((elt, 1))
    def max(self):
        if self.size() == 0:
            return None
        (max, _n) = self.ll_max.next.elt
        return max
    def pop(self) -> Optional[Any]:
        node = self.ll.next
        elt = node.elt if node else None
        self.ll.delete_after()
        if self.size() == 0:
            self.ll_max.delete_after()
            return elt
        (max_cur, n) = self.ll_max.next.elt
        if elt == max_cur:
            self.ll_max.delete_after()
            if n > 1:
                self.ll_max.insert((max_cur, n-1))

        return elt
    def __repr__(self):
        elts = []
        node = self.ll_max
        while node.next:
            elts.append(repr(node.next.elt))
            node = node.next
            if node.next is None:
                break
        ll_repr = super().__repr__()
        ll_max_repr = "ll_max(%s)" % (", ".join(elts))
        return "%s (%s)" % (ll_repr, ll_max_repr)
    def __eq__(self, other) -> bool:
        return self.ll == other.ll \
            and self.ll_max == other.ll_max
