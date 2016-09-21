import qctests.EN_constant_value_check

import util.testingProfile
import numpy
import util.main as main

#### EN_constant_value_check -------------------------------------------

class TestClass():

    parameters = {
        "table": 'unit'
    }

    def setUp(self):
        # this qc test will go looking for the profile in question in the db, needs to find something sensible
        main.faketable('unit')
        main.fakerow('unit')

    def tearDown(self):
        main.dbinteract('DROP TABLE unit;')

    def test_EN_constant_value_threshold(self):
        '''
        check EN_constant_value is flagging 90% and above.
        '''

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [100,200,300,400,500,600,700,800,900,1000], uid=8888)
        qc = qctests.EN_constant_value_check.test(p, self.parameters)
        truth = numpy.ones(10, dtype=bool)
        assert numpy.array_equal(qc, truth), 'failing to flag when exactly 90% of measurements are identical'

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,10,10], [100,200,300,400,500,600,700,800,900,1000], uid=8888)
        qc = qctests.EN_constant_value_check.test(p, self.parameters)
        truth = numpy.zeros(10, dtype=bool)
        assert numpy.array_equal(qc, truth), 'incorrectly flagging when less than 90% of measurements are identical'    

    def test_EN_constant_value_spacing(self):
        '''
        check EN_constant_value is requiring identical values to cover at least 100 m range
        '''

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [1,2,3,4,5,6,7,8,9,10], uid=8888)
        qc = qctests.EN_constant_value_check.test(p, self.parameters)
        truth = numpy.zeros(10, dtype=bool)
        assert numpy.array_equal(qc, truth), 'incorrectly flagging identical measurements that do not span 100 m of depth.'

    def test_EN_constant_value_missing_depth(self):
        '''
        Ensures EN_constant_value is not getting thrown by missing depths
        '''

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,None], uid=8888)
        qc = qctests.EN_constant_value_check.test(p, self.parameters)
        truth = numpy.ones(10, dtype=bool)
        assert numpy.array_equal(qc, truth), 'failing to flag when the deepest depth in a run of constant temperature is missing.'