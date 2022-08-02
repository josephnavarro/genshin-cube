#! usr/bin/env python3
from uuid import uuid4
from typing import List, Dict, Set, Tuple
from src.utility import Utility


class BlockSystem:
    __slots__ = [
        "node_entity",
        "node_values",
        "answers",
        "targets",
        "store_cycles",
        "node_cycles",
        "node_static",
        "node_affect",
        "node_index",
        "node_maximum",
        "node_immune",
        "node_label",
        "node_initial"
    ]

    def __init__(self):
        self.node_affect: Dict[str, Set[str]] = {}
        self.node_cycles: Dict[str, str] = {}
        self.node_entity: Dict[str, str] = {}
        self.node_index: Dict[str, int] = {}
        self.node_maximum: Dict[str, int] = {}
        self.node_static: Dict[str, bool] = {}
        self.node_values: Dict[str, any] = {}
        self.node_immune: Dict[str, bool] = {}
        self.node_label: Dict[str, str] = {}
        self.node_initial: Dict[str, any] = {}
        self.answers: Dict[int, List[str]] = {}
        self.targets: Dict[str, any] = {}
        self.store_cycles: Dict[str, Tuple] = {}

    @staticmethod
    def is_duplicate(d_values: dict, s_states: set) -> bool:
        """ Returns true if system body is a traversed state; false otherwise.
        """
        return tuple(d_values.values()) in s_states

    def clear(self):
        """ Clears all local fields.
        """
        self.node_affect.clear()
        self.node_cycles.clear()
        self.node_entity.clear()
        self.node_index.clear()
        self.node_maximum.clear()
        self.node_static.clear()
        self.node_values.clear()
        self.node_label.clear()
        self.node_initial.clear()
        self.answers.clear()
        self.targets.clear()
        self.store_cycles.clear()

    def is_solved(self) -> bool:
        """ Returns true if system is solved; false otherwise.
        """
        return self._verify(self.node_values)

    def cycle_add(self, s_label: str, t_cycle: Tuple):
        """ Adds a cycle to the system.
        """
        self.store_cycles[s_label] = t_cycle

    def cycle_get(self, s_label: str) -> Tuple:
        """ Returns a cycle from the store given its label.
            Debugging only.
        """
        return self.store_cycles.get(s_label, [])

    def node_create(self, s_label: str):
        """ Adds a newly-labeled node to the system.
        """
        s_node: str = str(uuid4())
        self.node_entity[s_label] = s_node
        self.node_affect[s_node] = set()
        self.node_index[s_node] = 0
        self.node_label[s_node] = s_label
        self.node_maximum[s_node] = 0
        self.node_static[s_node] = False
        self.node_immune[s_node] = False

    def node_delete(self, s_label: str):
        """ Deletes a node given its label.
        """
        s_node: str = self.node_get(s_label)
        self.node_affect.pop(s_node, None)
        self.node_cycles.pop(s_node, None)
        self.node_index.pop(s_node, None)
        self.node_maximum.pop(s_node, None)
        self.node_static.pop(s_node, None)
        self.node_values.pop(s_node, None)
        self.node_entity.pop(s_label, None)
        self.node_initial.pop(s_label, None)

    def node_get(self, s_label: str) -> str:
        """ Returns a node (entity) given its label.
        """
        return self.node_entity.get(s_label)

    def node_get_affect(self, s_label: str) -> Set[str]:
        """ Returns nodes that are affected by the given node.
        """
        s_key: str = self.node_get(s_label)
        return self.node_affect.get(s_key)

    def node_get_index(self, s_key: str) -> int:
        """ Returns current index of a node given its ID.
            Debugging only.
        """
        return self.node_index.get(s_key)

    def node_get_label(self, s_key: str) -> str:
        """ Returns label of node given its ID.
        """
        return self.node_label.get(s_key)

    def node_set_value(self, s_label: str, value: any):
        """ Sets the value of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        self.node_values[s_node] = value
        self.node_initial[s_node] = value
        try:
            s_cycle: str = self.node_cycles[s_node]
            t_cycle: Tuple = self.store_cycles[s_cycle]
            self.node_index[s_node] = t_cycle.index(value)
        except KeyError:
            pass

    def node_get_initial(self, s_label: str):
        """ Returns the initial value of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        return self.node_initial[s_node]

    def node_set_cycle(self, s_label: str, s_cycle: str):
        """ Sets the cycle (key) of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        self.node_cycles[s_node] = s_cycle
        t_cycle: Tuple = self.store_cycles[s_cycle]
        self.node_maximum[s_node] = len(t_cycle) - 1
        try:
            v_value = self.node_values[s_node]
            self.node_index[s_node] = t_cycle.index(v_value)
        except KeyError:
            pass

    def node_set_static(self, s_label: str, static: bool):
        """ Sets the static flag of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        self.node_static[s_node] = static

    def node_get_static(self, s_label: str) -> bool:
        """ Gets the static flag of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        return self.node_static.get(s_node)

    def node_set_immune(self, s_label: str, immune: bool):
        """ Sets the immune flag of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        self.node_immune[s_node] = immune

    def node_get_immune(self, s_label: str) -> bool:
        """ Gets the immune flag of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        return self.node_immune.get(s_node)

    def node_set_target(self, s_label: str, value):
        """ Sets the target value of a given labeled node.
        """
        s_node: str = self.node_get(s_label)
        self.targets[s_node] = value

    def best_answers(self) -> list:
        """ Returns a list of best answers for the system.
        """
        if not self.answers:
            return ["No solution!"]
        else:
            answer_keys = Utility.dict_keys_in_order(self.answers)
            return self.answers[min(answer_keys)]

    def best_length(self) -> int:
        """ Returns length of best answer.
        """
        if not self.answers:
            return -1
        else:
            return min(Utility.dict_keys_in_order(self.answers))

    def node_update(
          self,
          s_key: str,
          d_values: Dict[str, any],
          d_index: Dict[str, int]
    ) -> Tuple[Dict[str, any], Dict[str, int]]:
        """ 'Updates' a single node.
        """
        try:
            i_index: int = d_index[s_key]
            i_max: int = self.node_maximum[s_key]
            b_static: bool = self.node_static[s_key]
            s_cycle: str = self.node_cycles[s_key]
            t_cycle: Tuple = self.store_cycles[s_cycle]
            if b_static:
                i_newindex = i_index
            elif i_index >= i_max:
                i_newindex = 0
            else:
                i_newindex = i_index + 1
            v_newval: any = t_cycle[i_newindex]
            d_values[s_key] = v_newval
            d_index[s_key] = i_newindex
        except KeyError:
            pass

        return d_values, d_index

    def node_hit(
          self,
          s_label: str,
          d_values: Dict[str, any] = {},
          d_index: Dict[str, int] = {}
    ) -> Tuple[Dict[str, any], Dict[str, int]]:
        """ Simulates hitting a given labeled node.
        """
        s_center: str = self.node_get(s_label)
        d_values = d_values.copy() if d_values else self.node_values
        d_index = d_index.copy() if d_index else self.node_index
        b_immune: bool = self.node_immune.get(s_center)
        if not b_immune:
            try:
                for s_affected in self.node_affect[s_center]:
                    d_values, d_index = self.node_update(s_affected, d_values, d_index)
                d_values, d_index = self.node_update(s_center, d_values, d_index)
            except (KeyError, AttributeError):
                pass
        return d_values, d_index

    def node_link_single(self, k1: str, k2: str):
        """ Creates a unidirectional link from node k1 to node k2.
        """
        n1: str = self.node_get(k1)
        n2: str = self.node_get(k2)
        self.node_affect[n1].add(n2)

    def node_link_double(self, k1: str, k2: str):
        """ Creates a bidirectional link between node k1 and node k2.
        """
        self.node_link_single(k1, k2)
        self.node_link_single(k2, k1)

    def search_solutions(self, max_iters: int, *, comprehensive=False, verbose=False):
        """ Steps up incrementally to determine the shortest possible solutions for the puzzle.
        """
        iteration = 0
        while not self.answers and iteration < max_iters:
            iteration += 1
            self._solve1(iteration, comprehensive=comprehensive, verbose=verbose)

    def _solve1(self, threshold: int, *, comprehensive=False, verbose=False):
        """ Solves the system.
        """
        for s_nodelabel, s_nodeid in self.node_entity.items():
            s_states = set()
            s_states.add(tuple(self.node_values.values()))

            d_values, d_index = self.node_hit(s_nodelabel, self.node_values, self.node_index)
            l_chain: List[str] = [s_nodelabel]
            if verbose:
                print("".join(l_chain))

            if self._verify(d_values):
                Utility.add_to_dict(self.answers, len(l_chain), l_chain)
            else:
                self._solve2(threshold, d_values, d_index, s_states, l_chain, comprehensive=comprehensive, verbose=verbose)

    def _solve2(
          self,
          threshold: int,
          d_values: Dict[str, any],
          d_index: Dict[str, int],
          s_states: Set[Tuple[any]],
          l_chain: List[str],
          *,
          comprehensive: bool = False,
          verbose: bool = False
    ):
        """ Recursive helper method to solve the system.
        """
        if len(l_chain) < threshold:
            s_current_state: Tuple = tuple(d_values.values())
            s_states.add(s_current_state)

            for s_nodelabel, s_nodeid in self.node_entity.items():
                d2_values, d2_index = self.node_hit(s_nodelabel, d_values, d_index)
                l2_chain: List[str] = l_chain[:]

                if not self.is_duplicate(d2_values, s_states):
                    l2_chain.append(s_nodelabel)
                    if verbose:
                        print("".join(l2_chain))
                    if self._verify(d2_values):
                        Utility.add_to_dict(self.answers, len(l2_chain), l2_chain)
                    else:
                        self._solve2(threshold, d2_values, d2_index, s_states, l2_chain, comprehensive=comprehensive, verbose=verbose)

            if comprehensive:
                s_states.remove(s_current_state)

    def _verify(self, d_values: Dict[str, any]) -> bool:
        """ If targets exist, returns true if all node values equal their respective targets.
            If targets do not exist, returns true if all node values are equal to each other.
            Returns false otherwise.
        """
        if self.targets:
            return all(d_values.get(x, None) == self.targets.get(x) for x in self.targets)
        else:
            t_items: Tuple = tuple(d_values.values())
            return all(x == t_items[0] for x in t_items)
