#! usr/bin/env python3
from src.utility import Utility
from copy import copy, deepcopy


class Node:
    __slots__ = [
        "static",
        "_affects",
        "_cycle",
        "_index",
        "_label",
        "_maximum",
        "_value"
    ]

    def __init__(self, label: str):
        self.static: bool = False
        self._affects: set = set()
        self._cycle: list = [Utility.null()]
        self._index: int = 0
        self._label: str = label
        self._maximum: int = 0
        self._value = Utility.null()

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.value == other.value
        return False

    def __ne__(self, other):
        if isinstance(other, Node):
            return self.value != other.value
        return True

    def __copy__(self):
        return self._update(self.index)

    def __deepcopy__(self, memo):
        return copy(self)

    @property
    def affects(self) -> set:
        """ (Read-only). Returns the set of nodes (labels) this node affects unidirectionally.
        """
        return self._affects.copy()

    @property
    def index(self) -> int:
        """ (Read-only). Returns this node's current index into its cycle.
        """
        return self._index

    @property
    def label(self) -> str:
        """ (Read-only). Returns this node's current label.
        """
        return self._label

    @property
    def maximum(self) -> int:
        """ (Read-only). Returns the maximum possible cycle index for this node.
        """
        if self._maximum < 1:
            self._maximum = len(self.cycle) - 1
        return self._maximum

    @property
    def value(self):
        """ (Read-only). Returns the current value for this node.
        """
        return self.cycle[self.index]

    @property
    def cycle(self) -> list:
        """ (Read-only). Returns the value cycle associated with this node.
        """
        return deepcopy(self._cycle)

    def affect(self, other):
        """ Establishes a unidirectional relationship to another node.
        """
        self._affects.add(other.label)

    def set_cycle(self, cycle: list):
        """ Records a new value cycle.
        """
        self._cycle = deepcopy(cycle)
        self._set_index()

    def set_static(self, static: bool):
        """ Sets this node's static flag.
        """
        self.static = static

    def set_value(self, value):
        """ Sets this node's value.
        """
        self._value = value
        self._set_index()

    def update(self):
        """ Returns a new node representing one iteration past this node's current value.
        """
        i_index: int = self.index
        i_max: int = self.maximum
        b_static: bool = self.static

        if b_static:
            return self._update(i_index)
        elif i_index >= i_max:
            return self._update(0)
        else:
            return self._update(i_index + 1)

    def _update(self, index: int):
        """ Returns a new node.
        """
        new_node = Node(self.label)
        new_value = self.cycle[index]
        new_node.set_value(new_value)
        new_node.set_cycle(self.cycle)
        new_node.set_static(self.static)
        new_node._set_affects(self.affects)
        return new_node

    def _set_affects(self, affects: set):
        """ Overwrites list of affected nodes.
        """
        self._affects = affects

    def _set_index(self):
        """ Updates local cycle index based on value.
        """
        try:
            self._index: int = self._cycle.index(self._value)
        except (IndexError, ValueError):
            self._index: int = 0
