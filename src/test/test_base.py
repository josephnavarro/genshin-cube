#! usr/bin/env python3


class TestBase:
    """ Base class for a generic test suite.
    """

    @staticmethod
    def test_ascertain(flag: bool):
        if flag:
            print("Success~")
        else:
            print("Failure.")