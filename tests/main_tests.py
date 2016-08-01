import util.main as main
import os

class TestClass():

    def importQC_test(self):
        '''
        make sure main.importQC returns a valid list of tests that actually exist
        '''

        tests = main.importQC("qctests")
        assert isinstance(tests, list), 'importQC did not return a list'

        for test in tests:
            assert os.path.isfile('qctests/'+test+'.py'), 'test ' + test + ' is not found.'




