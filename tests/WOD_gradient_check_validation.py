import qctests.WOD_gradient_check

import util.testingProfile
import numpy

##### WOD_gradient_check ---------------------------------------------------

def test_WOD_gradient_check_temperature_inversion():
    '''
    validate temperaure inversion behavior
    '''

    # should just barely pass; gradient exactly at threshold
    p = util.testingProfile.fakeProfile([100, 130], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged temperature inversion at threshold'    

    # should just barely fail; gradient slightly over threshold
    p = util.testingProfile.fakeProfile([100, 130.00001], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag slight excess temperature inversion' 

def test_WOD_gradient_check_temperature_gradient():
    '''
    validate temperaure gradient behavior
    '''

    # should just barely pass; gradient exactly at threshold
    p = util.testingProfile.fakeProfile([100, 30], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged temperature gradient at threshold'    

    # should just barely fail; inversion slightly over threshold
    p = util.testingProfile.fakeProfile([100, 29.9999], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag slight excess temperature gradient' 
