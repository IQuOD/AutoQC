import qctests.EN_increasing_depth_check

import util.testingProfile
import numpy as np
import util.main as main

#### EN_increasing_depth_check -------------------------------------------

class TestClass():
    parameters = {}
    parameters['dbTable'] = 'demo'

    def setUp(self):
        main.demoTable(raw='', truth=False, uid=8888, year=1999, month=12, day=31, time=23.99, lat=0, long=0, cruise=1234, probe=0)

    def tearDown(self):
        main.dbinteract('drop table demo;')    

    def test_EN_increasing_depth_outside_valid_range(self):
        '''
        Check EN_increasing_depth_check flags values < 0 and > 11000m.
        '''

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [-1,200,300,400,500,600,700,800,900,1000], uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.zeros(10, dtype=bool)
        truth[0] = True
        assert np.array_equal(qc, truth), 'Failed to flag depth < 0'

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,11001], uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.zeros(10, dtype=bool)
        truth[-1] = True
        assert np.array_equal(qc, truth), 'Failed to flag depth > 11000'    

    def test_EN_increasing_depth_flagging(self):
        '''
        Check EN_increasing_depth_check flags incorrect depths.
        '''

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,500,500,600,700,800,900,1000], latitude=0.0, uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.zeros(10, dtype=bool)
        truth[3:5] = True
        assert np.array_equal(qc, truth), 'Failed to constant depth'

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,510,500,600,700,800,900,1000], latitude=0.0, uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.zeros(10, dtype=bool)
        truth[3:5] = True
        assert np.array_equal(qc, truth), 'Failed to incorrect depths when cannot determine which is wrong'

        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,610,500,600,700,800,900,1000], latitude=0.0, uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.zeros(10, dtype=bool)
        truth[3] = True
        print qc
        assert np.array_equal(qc, truth), 'Failed to incorrect depth'

    def test_EN_increasing_depth_all_zero(self):
        '''
        Check EN_increasing_depth_check flags all levels in a profile with all depths = 0
        '''

        p = util.testingProfile.fakeProfile([0]*1000, [0]*1000, uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        truth = np.ones(1000, dtype=bool)

        print qc, truth

        assert np.array_equal(qc, truth), 'Failed to flag all levels in profile with all 0 depths'  

