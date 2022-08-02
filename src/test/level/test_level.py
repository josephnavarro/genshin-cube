#! usr/bin/env python3
from src.level import Level
from src.block_system import BlockSystem
from src.level_interface import LevelInterface
from src.level_image import LevelImage
from src.utility import Utility
from src.test.test_base import TestBase


class TestLevel(TestBase):
    """ Test suite for level creation.
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
    def test_read_from_script(cls):
        s: BlockSystem = BlockSystem()
        i: LevelInterface = LevelInterface()
        im: LevelImage = LevelImage()
        Level.from_script(s, i, im, Utility.abspath(__file__, "DUMMY_2.CCP"), headless=True)
        # Level.from_script(s, i, im, Utility.abspath(__file__, "DUMMY_1.CCP"), headless=True)
        s.search_solutions(50)
        cls.test_verify_solved(s)
        print(s.best_length())
        # cls.test_ascertain(s.best_length() == 9)


if __name__ == "__main__":
    TestLevel.test_read_from_script()
