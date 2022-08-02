#! usr/bin/env python3
from src.utility_image import ImageUtil
from src.test.test_base import TestBase


class TestUtility(TestBase):
    """ Test suite for utility methods.
    """

    @classmethod
    def test_hydrate(cls):
        x = "fcf0f0f0f0f0f0f0f0f0f0f0f0f0f0f3ccfcffffffffffffffffffffffffff33cccc0fffffffffffffffffffffffff33ccfcf0fcf"
        "0fcf0fcf0fcf0ffffffff33ccccc0ffcccc3bce00cc3bffffffff33ccfcf0fcf0fcf0fcfcfcf0ffffffff33cccec2ccc0ccc0cc0cccc0"
        "ffffffff33ccfcf0fcf0fcf0fcfffcf0ffffffff33ccccc0ccc0cc34cc0fcef0ffffffff33ccfcfcfcf0fffffcf0fcffffffffff33ccf"
        "ffffc3cffffcc30cc0fffffffff33ccfffffffffffffcf0fffcffffffff33ccffffffffffffcc70cc0fffffffff33ccfffffffffffffc"
        "f0ffffffffffff33ccffffffffffffcc33ffffffffffff33cf0f0f0f0f0f0f0f0f0f0f0f0f0f0f3f"
        y = ImageUtil.dessicate(x)
        z = ImageUtil.hydrate(y)
        cls.test_ascertain(x == z)


if __name__ == "__main__":
    TestUtility.test_hydrate()
