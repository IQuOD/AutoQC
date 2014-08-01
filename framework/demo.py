import glob
import unittest
import sys
import os
from ddt import ddt, FILE_ATTR
import tests
import numpy as np

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
class TestClass(unittest.TestCase):
    pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestClass)
results = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# Generate a table of results. The table contains True if the test was
# failed for a data point (consistent with how a mask is defined in 
# numpy masked arrays).
nTests = len(testNames)
nData  = results.testsRun / nTests
table = np.ndarray([nTests, nData], dtype=bool)
table[:, :] = False

testNameIndices = {}
for iName, name in enumerate(testNames): 
    testNameIndices[name] = iName

failedTests = [failure[0].id() for failure in results.failures]
for failedTest in failedTests:
    pos = failedTest.find('TestClass.test_')
    failedTest = failedTest[pos + 15:]
    pos = failedTest.rfind('_')
    failureName = failedTest[:pos]
    failureData = failedTest[pos+1:]
    table[testNameIndices[failureName], int(failureData)] = True

for i, name in enumerate(testNames):
    print name, table[i, :]
