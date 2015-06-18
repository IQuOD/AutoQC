import qctests.Argo_regional_range_test

import util.testingProfile
import numpy

##### Argo_regional_range_test -----------------------------------------

def Argo_regional_range_test_mediterranean_hot():
    '''
    make sure ARRT is flagging mediterranean temps that are too hot
    '''

    p = util.testingProfile.fakeProfile([40.1, 39.9], [10, 20], 35., 18.) 
    qc = qctests.Argo_regional_range_test.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag hot temperatures in Mediterranean Sea'   

def Argo_regional_range_test_red_cold():
    '''
    make sure ARRT is flagging red sea temps that are too cold
    '''

    p = util.testingProfile.fakeProfile([21.6, 21.8], [10, 20], 22., 38.) 
    qc = qctests.Argo_regional_range_test.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag cold temperatures Red Sea' 

def Argo_regional_range_test_isInRegion():
    '''
    Check a few near misses for isInRegion
    '''

    redSeaLat  = [10., 20., 30., 10.]
    redSeaLong = [40., 50., 30., 40.]
    mediterraneanLat  = [30., 30., 40., 42., 50., 40., 30]
    mediterraneanLong = [6.,  40., 35., 20., 15., 5.,  6.]

    assert qctests.Argo_regional_range_test.isInRegion(43.808479, 7.445307, mediterraneanLat, mediterraneanLong) == False, '43.808479, 7.445307 should not be flagged as in the Mediterranean'
    assert qctests.Argo_regional_range_test.isInRegion(30.540632, 34.705133, redSeaLat, redSeaLong) == False, '30.540632, 34.705133 should not be flagged as in the Red Sea'