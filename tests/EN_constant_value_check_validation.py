import qctests.EN_constant_value_check

import util.testingProfile
import numpy

#### EN_constant_value_check -------------------------------------------

def test_EN_constant_value_threshold():
    '''
    check EN_constant_value is flagging 90% and above.
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [100,200,300,400,500,600,700,800,900,1000])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.ones(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failing to flag when exactly 90% of measurements are identical'

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,10,10], [100,200,300,400,500,600,700,800,900,1000])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.zeros(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging when less than 90% of measurements are identical'    

def test_EN_constant_value_spacing():
    '''
    check EN_constant_value is requiring identical values to cover at least 100 m range
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [1,2,3,4,5,6,7,8,9,10])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.zeros(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging identical measurements that do not span 100 m of depth.'

def test_EN_constant_value_missing_depth():
    '''
    Ensures EN_constant_value is not getting thrown by missing depths
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,None])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.ones(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failing to flag when the deepest depth in a run of constant temperature is missing.'