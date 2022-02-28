#! /usr/bin/env python3

import unittest
from enum import IntFlag


class FakeEnums(IntFlag):

    ENUM_1 = (1 << 128)


class TestFlags(unittest.TestCase):

    def test_large_enum(self):
        '''Test that an enum can be very large.'''

        self.assertEqual(FakeEnums.ENUM_1, 2 ** 128)
        self.assertEqual(FakeEnums.ENUM_1, 340282366920938463463374607431768211456)


if __name__ == '__main__':
    unittest.main()
