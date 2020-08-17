import qctests.IQuOD_gross_range_check
import util.testingProfile
import numpy
from util import obs_utils

##### IQuOD_gross_range_check ---------------------------------------------------

def test_IQuOD_gross_range_check():
    '''
    Make sure the test is flagging temperature excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([-4.000000001], [100]) 
    qc = qctests.IQuOD_gross_range_check.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly colder than -4.0 C'

    # -4.0 OK
    p = util.testingProfile.fakeProfile([-4.0], [100]) 
    qc = qctests.IQuOD_gross_range_check.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging -4.0 C'

    # 100.0 OK
    p = util.testingProfile.fakeProfile([100], [100]) 
    qc = qctests.IQuOD_gross_range_check.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging 100 C'

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([100.0000001], [100], latitude=0.0) 
    qc = qctests.IQuOD_gross_range_check.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly warmer than 100 C'        

    # test of a sequence of temperatures contained in a profile
    p = util.testingProfile.fakeProfile([0.0, 20.0, -5.0, 16.0, 101.0], [0, 1, 2, 3, 4, 5], latitude=0.0) 
    qc = qctests.IQuOD_gross_range_check.test(p, None)
    truth = numpy.zeros(5, dtype=bool)
    truth[2] = True
    truth[4] = True
    assert numpy.array_equal(qc, truth), 'failed to flag values in a profile'  
    
          

