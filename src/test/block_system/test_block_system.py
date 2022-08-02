#! usr/bin/env python3
from src.block_system import BlockSystem
from src.test.test_base import TestBase


class TestBlockSystem(TestBase):
    """ Test suite for block solving system.
    """

    @classmethod
    def test_execute_answer(cls, s: BlockSystem):
        for s_key in s.best_answers()[0]:
            s.node_hit(s_key)

    @classmethod
    def test_verify_solved(cls, s: BlockSystem):
        cls.test_execute_answer(s)
        cls.test_ascertain(s.is_solved())

    @classmethod
    def test_verify_not_solved(cls, s: BlockSystem):
        cls.test_execute_answer(s)
        cls.test_ascertain(not s.is_solved())

    @classmethod
    def test_cycle_order_independence(cls):
        s = BlockSystem()
        s_cycle = "main"
        s_value = "2"

        s.cycle_add(s_cycle, ("1", s_value))

        s.node_create("A")
        s.node_set_cycle("A", s_cycle)
        s.node_set_value("A", s_value)

        s.node_create("B")
        s.node_set_value("B", s_value)
        s.node_set_cycle("B", s_cycle)

        n_a = s.node_get("A")
        n_b = s.node_get("B")
        l_c = s.cycle_get(s_cycle)

        cls.test_ascertain(s.node_get_index(n_a) == s.node_get_index(n_b) == l_c.index(s_value))

    @classmethod
    def basic_test(cls):
        s = BlockSystem()
        s.cycle_add("main", ("1", "2", "3"))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_set_value("A", "1")
        s.node_set_value("B", "2")
        s.node_set_value("C", "3")
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.node_link_double("A", "B")
        s.node_link_double("B", "C")
        s.search_solutions(10)
        cls.test_verify_solved(s)
        cls.test_ascertain(s.best_length() == 3)

    @classmethod
    def new_linear_test(cls):
        s = BlockSystem()
        s.cycle_add("main", (1, 2, 3, 4))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_create("D")
        s.node_create("E")
        s.node_set_value("A", 1)
        s.node_set_value("B", 3)
        s.node_set_value("C", 3)
        s.node_set_value("D", 4)
        s.node_set_value("E", 4)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.node_set_cycle("D", "main")
        s.node_set_cycle("E", "main")
        s.node_link_single("A", "C")
        s.node_link_single("C", "A")
        s.node_link_single("C", "E")
        s.node_link_single("E", "C")
        s.node_link_single("B", "A")
        s.node_link_single("B", "C")
        s.node_link_single("D", "C")
        s.node_link_single("D", "E")
        s.search_solutions(10, comprehensive=True)
        cls.test_verify_solved(s)
        cls.test_ascertain(s.best_length() == 5)

    @classmethod
    def static_test(cls):
        s = BlockSystem()
        s.cycle_add("main", (1, 2, 3, 4))
        s.node_create("A")
        s.node_create("B")
        s.node_set_value("A", 1)
        s.node_set_value("B", 2)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_static("A", True)
        s.search_solutions(10)
        cls.test_verify_solved(s)
        cls.test_ascertain(s.best_length() == 3)

    @classmethod
    def singles_test(cls):
        s = BlockSystem()
        s.cycle_add("main", (1, 2, 3))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_set_value("A", 1)
        s.node_set_value("B", 2)
        s.node_set_value("C", 3)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.search_solutions(10)
        cls.test_verify_solved(s)
        cls.test_ascertain(s.best_length() == 3)

    @classmethod
    def test2(cls):
        s = BlockSystem()
        s.cycle_add("main", (1, 2, 3, 4))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_create("D")
        s.node_create("E")
        s.node_set_value("A", 3)
        s.node_set_value("B", 4)
        s.node_set_value("C", 1)
        s.node_set_value("D", 2)
        s.node_set_value("E", 3)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.node_set_cycle("D", "main")
        s.node_set_cycle("E", "main")
        s.node_set_static("E", True)
        s.node_set_target("A", 3)
        s.node_set_target("B", 3)
        s.node_set_target("C", 3)
        s.node_set_target("D", 3)
        s.node_set_target("E", 3)
        s.node_link_double("A", "B")
        s.node_link_double("B", "C")
        s.node_link_double("C", "D")

        # import time
        # start_time = time.time()
        s.search_solutions(20)
        # print("Time elapsed: {}".format(time.time() - start_time))
        # print("Shortest solution: {} moves".format(s.best_length()))
        # from utility import Utility
        # Utility.print_list(s.best_answers())

        cls.test_verify_solved(s)

    @classmethod
    def nan_test1(cls):
        s = BlockSystem()
        s.node_set_target("A", 1)
        s.search_solutions(10)
        cls.test_verify_not_solved(s)

    @classmethod
    def nan_test2(cls):
        s = BlockSystem()
        s.node_create("A")
        s.node_set_target("A", 1)
        s.search_solutions(10)
        cls.test_verify_not_solved(s)

    @classmethod
    def test_delete(cls):
        s = BlockSystem()
        s.node_create("A")
        s.node_delete("A")
        cls.test_ascertain(not s.node_get("A"))

    @classmethod
    def test_delete_resilience(cls):
        s = BlockSystem()
        s.cycle_add("main", ("1", "2", "3"))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_create("D")
        s.node_set_value("A", "1")
        s.node_set_value("B", "2")
        s.node_set_value("C", "3")
        s.node_set_value("D", "1")
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.node_set_cycle("D", "main")
        s.node_link_double("A", "B")
        s.node_link_double("B", "C")
        s.node_link_double("C", "D")
        s.node_delete("D")
        s.search_solutions(10)
        cls.test_verify_solved(s)

    @classmethod
    def new_linear_test2(cls):
        s = BlockSystem()
        s.cycle_add("main", (1, 2, 3, 4))
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_create("D")
        s.node_set_value("A", 1)
        s.node_set_value("B", 3)
        s.node_set_value("C", 4)
        s.node_set_value("D", 1)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.node_set_cycle("D", "main")
        s.node_link_double("A", "B")
        s.node_link_double("B", "C")
        s.node_link_double("C", "D")
        s.search_solutions(10, comprehensive=True)
        cls.test_verify_solved(s)
        print(s.best_answers())


if __name__ == "__main__":
    TestBlockSystem.test_delete()
    TestBlockSystem.test_delete_resilience()
    TestBlockSystem.test_cycle_order_independence()
    TestBlockSystem.nan_test1()
    TestBlockSystem.nan_test2()
    TestBlockSystem.basic_test()
    TestBlockSystem.new_linear_test()
    TestBlockSystem.static_test()
    TestBlockSystem.singles_test()
    TestBlockSystem.test2()
    TestBlockSystem.new_linear_test2()
    print("All tests done.")
