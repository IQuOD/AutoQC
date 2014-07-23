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
        self.assertEqual(value%2, 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestName)
results = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)