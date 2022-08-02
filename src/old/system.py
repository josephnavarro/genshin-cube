#! usr/bin/env python3
from src.old.node import Node
from copy import deepcopy
from src.utility import Utility


class System:
    THRESHOLD = 5

    class DummyNode(Node):
        def __init__(self):
            super().__init__("")

    __slots__ = [
        "body",
        "answers",
        "targets",
        "cycles",
        "threshold"
    ]

    def __init__(self):
        self.body: dict = {}
        self.answers: dict = {}
        self.targets: dict = {}
        self.cycles: dict = {}
        self.threshold: int = System.THRESHOLD

    @staticmethod
    def is_duplicate(d_body: dict, s_states: set) -> bool:
        """ Returns true if system body is a traversed state; false otherwise.
        """
        return tuple(d_body.values()) in s_states

    def is_solved(self) -> bool:
        """ Returns true if system is solved; false otherwise.
        """
        return self._verify(self.body)

    def cycle_add(self, s_label: str, l_cycle: list):
        """ Adds a cycle to the system.
        """
        self.cycles[s_label] = deepcopy(l_cycle)

    def cycle_get(self, s_label: str) -> list:
        return deepcopy(self.cycles.get(s_label, []))

    def node_create(self, s_label: str):
        """ Adds a newly-labeled node to the system.
        """
        self.body[s_label] = Node(s_label)

    def node_get(self, s_label: str) -> Node:
        """ Returns a node given its label.
        """
        return self.body.get(s_label)

    def node_set_value(self, s_label: str, value):
        """ Sets the value of a given labeled node.
        """
        n_node: Node = self.body.get(s_label)
        n_node.set_value(value)

    def node_set_cycle(self, s_label: str, s_cycle: str):
        """ Sets the cycle (key) of a given labeled node.
        """
        l_cycle: list = self.cycle_get(s_cycle)
        n_node: Node = self.node_get(s_label)
        n_node.set_cycle(l_cycle)

    def node_set_static(self, s_label: str, static: bool):
        """ Sets the static flag of a given labeled node.
        """
        n_node: Node = self.node_get(s_label)
        n_node.set_static(static)

    def node_set_target(self, s_label: str, value):
        """ Sets the target value of a given labeled node.
        """
        self.targets[s_label] = value

    def best_answers(self) -> list:
        """ Returns a list of best answers for the system.
        """
        if not self.answers:
            return ["No solution!"]
        else:
            answer_keys = Utility.dict_keys_in_order(self.answers)
            return self.answers[min(answer_keys)]

    def node_hit(self, s_label: str, d_items: dict = {}) -> dict:
        """ Simulates hitting a given labeled node.
        """
        if not d_items:
            d_items = self.body
        else:
            d_items = deepcopy(d_items)

        try:
            n_center: Node = d_items.get(s_label)
            for s_affected in n_center.affects:
                n_affected: Node = d_items.get(s_affected)
                d_items[s_affected] = n_affected.update()
            d_items[s_label] = n_center.update()
        except (KeyError, AttributeError):
            pass

        return d_items

    def node_link_single(self, k1: str, k2: str):
        """ Creates a unidirectional link from node k1 to node k2.
        """
        n1: Node = self.node_get(k1)
        n2: Node = self.node_get(k2)
        n1.affect(n2)

    def node_link_double(self, k1: str, k2: str):
        """ Creates a bidirectional link between node k1 and node k2.
        """
        self.node_link_single(k1, k2)
        self.node_link_single(k2, k1)

    def set_threshold(self, i_threshold: int):
        """ Sets maximum plies for answer calculation.
        """
        self.threshold = i_threshold

    def solve(self):
        """ Solves the system.
        """
        for s_key, n_val in self.body.items():
            s_states = set()
            s_states.add(tuple(self.body.values()))

            s_label: str = n_val.label
            d_body: dict = self.node_hit(s_label, self.body)
            l_chain: list = [s_label]

            if self._verify(d_body):
                Utility.add_to_dict(self.answers, len(l_chain), l_chain)
            else:
                self._solve(d_body, s_states, l_chain)

    def _solve(self, d_body: dict, s_states: set, l_chain: list):
        """ Recursive helper method to solve the system.
        """
        if len(l_chain) < self.threshold:
            s_states.add(tuple(d_body.values()))

            for s_key, n_val in d_body.items():
                s_label: str = n_val.label
                d_body_copy: dict = self.node_hit(s_label, d_body)
                l_chain_copy: list = l_chain[:]

                if not self.is_duplicate(d_body_copy, s_states):
                    l_chain_copy.append(s_label)

                    if self._verify(d_body_copy):
                        Utility.add_to_dict(self.answers, len(l_chain_copy), l_chain_copy)
                    else:
                        self._solve(d_body_copy, s_states.copy(), l_chain_copy)

    def _verify(self, d_items: dict) -> bool:
        """ If targets exist, returns true if all node values equal their respective targets.
            If targets do not exist, returns true if all node values are equal to each other.
            Returns false otherwise.
        """
        if self.targets:
            return all(
                d_items.get(x, System.DummyNode()).value == self.targets.get(x)
                for x in self.targets
            )
        else:
            l_items = list(d_items.values())
            return all(x == l_items[0] for x in l_items)
