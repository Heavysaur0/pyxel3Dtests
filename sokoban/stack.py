from typing import Iterable, Any

class StackNode:
    __slots__ = ('_next', '_value')

    def __init__(self, value = 0):
        self._next: None | StackNode = None
        self._value = value

    def __iter__(self):
        current = self
        while current is not None:
            yield current._value
            current = current._next


class Stack:
    __slots__ = ('_start', '_length')

    def __init__(self, values: Iterable | None = None):
        self._start = None
        self._length = 0
        if values:
            [self.append(value) for value in values]

    def __iter__(self):
        return iter([]) if self.is_empty() else iter(self._start)

    def __len__(self):
        return self._length

    def is_empty(self):
        return self._length == 0

    def pop(self) -> Any:
        if self.is_empty():
            raise IndexError("The stack is empty, cannot pop.")
        value = self._start._value
        self._start = self._start._next
        self._length -= 1
        return value

    def append(self, value):
        node = StackNode(value)
        node._next = self._start
        self._start = node
        self._length += 1

    def __repr__(self):
        return f"Stack<{', '.join(map(str, reversed(list(self))))}>"


if __name__ == "__main__":
    # Create a stack with values [1, 2, 3]
    s = Stack([1, 2, 3])  # Top of stack should be 3
    print(f"Tests on stack: {s}")

    # Test iteration order (LIFO: last-in, first-out)
    assert list(s) == [3, 2, 1], f"Expected [3, 2, 1], got {list(s)}"

    # Pop the top value
    popped = s.pop()
    assert popped == 3, f"Expected popped value to be 3, got {popped}"
    assert list(s) == [2, 1], f"Expected stack to be [2, 1], got {list(s)}"
    assert len(s) == 2, f"Expected stack to have length of 2, got {len(s)}"

    # Append a new value
    s.append(99)
    assert list(s) == [99, 2, 1], f"Expected stack to be [99, 2, 1], got {list(s)}"
    assert len(s) == 3, f"Expected stack to have length of 3, got {len(s)}"

    # Empty the stack
    assert not s.is_empty(), "Stack should not be empty"
    assert s.pop() == 99
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.is_empty(), "Stack should be empty after popping all elements"

    # Test popping from empty stack raises IndexError
    try:
        s.pop()
        assert False, "Expected IndexError when popping from empty stack"
    except IndexError:
        pass  # Expected

    print("All tests passed.")
