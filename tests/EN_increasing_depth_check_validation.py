import qctests.EN_increasing_depth_check

import util.testingProfile
import numpy as np

#### EN_increasing_depth_check -------------------------------------------

def test_EN_increasing_depth_outside_valid_range():
    '''
    Check EN_increasing_depth_check flags values < 0 and > 11000m.
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [-1,200,300,400,500,600,700,800,900,1000])
    qc = qctests.EN_increasing_depth_check.test(p)
    truth = np.zeros(10, dtype=bool)
    truth[0] = True
    assert np.array_equal(qc, truth), 'Failed to flag depth < 0'

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,11001])
    qc = qctests.EN_increasing_depth_check.test(p)
    truth = np.zeros(10, dtype=bool)
    truth[-1] = True
    assert np.array_equal(qc, truth), 'Failed to flag depth > 11000'    

def test_EN_increasing_depth_flagging():
    '''
    Check EN_increasing_depth_check flags incorrect depths.
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,500,500,600,700,800,900,1000], latitude=0.0)
    qc = qctests.EN_increasing_depth_check.test(p)
    truth = np.zeros(10, dtype=bool)
    truth[3:5] = True
    assert np.array_equal(qc, truth), 'Failed to constant depth'

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,510,500,600,700,800,900,1000], latitude=0.0)
    qc = qctests.EN_increasing_depth_check.test(p)
    truth = np.zeros(10, dtype=bool)
    truth[3:5] = True
    assert np.array_equal(qc, truth), 'Failed to incorrect depths when cannot determine which is wrong'

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,610,500,600,700,800,900,1000], latitude=0.0)
    qc = qctests.EN_increasing_depth_check.test(p)
    truth = np.zeros(10, dtype=bool)
    truth[3] = True
    print qc
    assert np.array_equal(qc, truth), 'Failed to incorrect depth'



