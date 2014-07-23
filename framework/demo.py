import unittest
import sys
import os
from ddt import ddt, file_data

dir = os.path.dirname(__file__)
datafile = os.path.join(dir, '../data/demo.json')
print datafile


@ddt
class TestName(unittest.TestCase):

    @file_data(datafile)
    def test_by_2(self, value):
        self.assertEqual(value % 2, 0)

    @file_data(datafile)
    def test_greater_five(self, value):
        self.assertEqual(value > 5, 0)

    @file_data(datafile)
    def test_by_3(self, value):
        self.assertEqual(value % 3, 1)

    @file_data(datafile)
    def test_equal_seven(self, value):
        self.assertEqual(value == 7, 0)

    @file_data(datafile)
    def test_less_zero(self, value):
        self.assertEqual(value < 0, 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestName)
results = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
