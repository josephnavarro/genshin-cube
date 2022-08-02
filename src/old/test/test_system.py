#! usr/bin/env python3
from src.old.system import System
from test_base import TestBase


class TestSystem(TestBase):
    @classmethod
    def test_execute_answer(cls, s: System):
        for s_key in s.best_answers()[0]:
            s.node_hit(s_key)

    @classmethod
    def test_verify_solved(cls, s: System):
        cls.test_execute_answer(s)
        cls.test_ascertain(s.is_solved())

    @classmethod
    def test_verify_not_solved(cls, s: System):
        cls.test_execute_answer(s)
        cls.test_ascertain(not s.is_solved())

    @classmethod
    def test_cycle_order_independence(cls):
        s = System()
        s_cycle = "main"
        s_value = "2"

        s.cycle_add(s_cycle, ["1", s_value])

        s.node_create("A")
        s.node_set_cycle("A", s_cycle)
        s.node_set_value("A", s_value)

        s.node_create("B")
        s.node_set_value("B", s_value)
        s.node_set_cycle("B", s_cycle)

        n_a = s.node_get("A")
        n_b = s.node_get("B")
        l_c = s.cycle_get(s_cycle)

        cls.test_ascertain(n_a.index == n_b.index == l_c.index(s_value))

    @classmethod
    def basic_test(cls):
        s = System()
        s.cycle_add("main", ["1", "2", "3"])
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
        s.solve()
        cls.test_verify_solved(s)

    @classmethod
    def new_linear_test(cls):
        s = System()
        s.cycle_add("main", [1, 2, 3, 4])
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
        s.solve()
        cls.test_verify_solved(s)

    @classmethod
    def static_test(cls):
        s = System()
        s.cycle_add("main", [1, 2, 3, 4])
        s.node_create("A")
        s.node_create("B")
        s.node_set_value("A", 1)
        s.node_set_value("B", 2)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_static("A", True)
        s.solve()
        cls.test_verify_solved(s)

    @classmethod
    def singles_test(cls):
        s = System()
        s.cycle_add("main", [1, 2, 3])
        s.node_create("A")
        s.node_create("B")
        s.node_create("C")
        s.node_set_value("A", 1)
        s.node_set_value("B", 2)
        s.node_set_value("C", 3)
        s.node_set_cycle("A", "main")
        s.node_set_cycle("B", "main")
        s.node_set_cycle("C", "main")
        s.solve()
        cls.test_verify_solved(s)

    @classmethod
    def test2(cls):
        s = System()
        s.cycle_add("main", [1, 2, 3, 4])
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
        s.set_threshold(10)
        s.node_link_double("A", "B")
        s.node_link_double("B", "C")
        s.node_link_double("C", "D")
        s.solve()
        cls.test_verify_solved(s)

    @classmethod
    def nan_test1(cls):
        s = System()
        s.node_set_target("A", 1)
        s.solve()
        cls.test_verify_not_solved(s)

    @classmethod
    def nan_test2(cls):
        s = System()
        s.node_create("A")
        s.node_set_target("A", 1)
        s.solve()
        cls.test_verify_not_solved(s)


if __name__ == "__main__":
    import time
    start_time = time.time()
    TestSystem.test_cycle_order_independence()
    TestSystem.nan_test1()
    TestSystem.nan_test2()
    TestSystem.basic_test()
    TestSystem.new_linear_test()
    TestSystem.static_test()
    TestSystem.singles_test()
    TestSystem.test2()
    print(time.time() - start_time)
    print("All tests done.")
