import qctests.Argo_impossible_location_test

import util.testingProfile
import numpy

##### Argo_impossible_location_test ---------------------------------------------------

def test_Argo_impossible_location_nominal_lat():
    '''
    check for flagging an out-of-range latitude
    '''
    p = util.testingProfile.fakeProfile([0], [0], 91, 0) 
    qc = qctests.Argo_impossible_location_test.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag latitude outside of range [-90, 90]'

def test_Argo_impossible_location_nominal_long():
    '''
    check for flagging an out-of-range long
    '''
    p = util.testingProfile.fakeProfile([0], [0], 0, 181) 
    qc = qctests.Argo_impossible_location_test.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag long outside of range [-180, 180]'