import glob
import unittest
import sys
import os
from ddt import ddt, FILE_ATTR
import tests

dir = os.path.dirname(__file__)
datafile = os.path.join(dir, '../data/demo.json')
print datafile

# Find all QC subroutines.
testFiles = glob.glob('tests/[!_]*.py')
print testFiles
testNames = [testFile[6:-3] for testFile in testFiles]
print testNames

# Define a decorator to convert the QC tests to the TestName class.
def include_tests(cls):
    for testName in testNames:
        exec('import tests.' + testName)
        exec('def test_' + testName + '(self, value): self.assertTrue(tests.' + testName + '.test(value))')
        exec('setattr(test_' + testName + ', FILE_ATTR, datafile)')
        exec('cls.test_' + testName + ' = test_' + testName)
    return cls

@ddt
@include_tests
class TestName(unittest.TestCase):
    pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestName)
results = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
