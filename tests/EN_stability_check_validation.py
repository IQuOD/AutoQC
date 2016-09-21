import qctests.EN_stability_check

import util.testingProfile
import numpy
import util.main as main

##### EN_stability_check ----------------------------------------------

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

    def test_mcdougallEOS(self):
        '''
        check the test values provided for the EOS in McDougall 2003
        '''

        eos = round(qctests.EN_stability_check.mcdougallEOS(35,25,2000), 6)
        assert  eos == 1031.654229, 'mcdougallEOS(35,25,2000) should be 1031.654229, instead got %f' % eos
        eos = round(qctests.EN_stability_check.mcdougallEOS(20,20,1000), 6)
        assert  eos == 1017.726743, 'mcdougallEOS(20,20,1000) should be 1017.726743, instead got %f' % eos
        eos = round(qctests.EN_stability_check.mcdougallEOS(40,12,8000), 6)
        assert  eos == 1062.928258, 'mcdougallEOS(40,12,8000) should be 1062.928258, instead got %f' % eos

    def test_mcdougall_potential_temperature(self):
        '''
        check the test values provided for the potential temperature approximation in McDougall 2003
        '''

        pt = round(qctests.EN_stability_check.potentialTemperature(35, 20, 2000), 6)
        assert pt == 19.621967, 'potential temperarure for S = 35 psu, T = 20C, p = 2000 db should be 19621967, instead got %f' % pt

    def test_EN_stability_check_padded(self):
        '''
        check some behavior near the test values provided in McDougall
        padded with the same level to avoid flagging the entire profile
        '''

        p = util.testingProfile.fakeProfile([13.5, 25.5, 20.4, 13.5, 13.5, 13.5, 13.5, 13.5, 13.5], [0, 10, 20, 30, 40, 50, 60, 70, 80], salinities=[40, 35, 20, 40, 40, 40, 40, 40, 40], pressures=[8000, 2000, 1000, 8000, 8000, 8000, 8000, 8000, 8000], uid=8888)
        qc = qctests.EN_stability_check.test(p, self.parameters)
        truth = numpy.ma.array([False, True, True, False, False, False, False, False, False], mask=False)
        assert numpy.array_equal(qc, truth), 'failed to flag padded stability example'


    def test_EN_stability_check_unpadded(self):
        '''
        check same four levels as above,
        but don't pad with extra levels, so that the whole profile ends up getting rejected at the last step.
        '''

        p = util.testingProfile.fakeProfile([13.5, 25.5, 20.4, 13.5], [0, 10, 20, 30], salinities=[40, 35, 20, 40], pressures=[8000, 2000, 1000, 8000], uid=8888)
        qc = qctests.EN_stability_check.test(p, self.parameters)
        truth = numpy.ma.array([True, True, True, True], mask=False)
        assert numpy.array_equal(qc, truth), 'failed to flag unpadded stability example'
