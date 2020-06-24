import util.main as main
import os

class TestClass:

    def importQC_test(self):
        '''
        make sure main.importQC returns a valid list of tests that actually exist
        '''

        tests = main.importQC("qctests")
        assert isinstance(tests, list), 'importQC did not return a list'

        for test in tests:
            assert os.path.isfile('qctests/'+test+'.py'), 'test ' + test + ' is not found.'

    def normalize_latitude_test(self):
        '''
        make sure latitude is mapped correctly
        '''

        assert 0 - main.normalize_latitude(0) < 0.000001
        assert 89 - main.normalize_latitude(91) < 0.000001
        assert -87 - main.normalize_latitude(-93) < 0.000001
        assert 50 - main.normalize_latitude(50) < 0.000001
        assert -30 - main.normalize_latitude(-30) < 0.000001


