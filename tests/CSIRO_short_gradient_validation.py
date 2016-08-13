import qctests.CSIRO_short_gradient
import util.testingProfile
import numpy

##### CSIRO_short_gradient ---------------------------------------------------

def test_CSIRO_short_gradient():
    '''
    Spot-check the nominal behavior of the CSIRO short gradient test.
    '''

    # nominal
    p = util.testingProfile.fakeProfile([0,1], [0,10]) 
    qc = qctests.CSIRO_short_gradient.test(p, None)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True

    assert numpy.array_equal(qc, truth), 'failed to flag a gradient at small delta-temp and delta-depth'

    p = util.testingProfile.fakeProfile([0,10], [0,100]) 
    qc = qctests.CSIRO_short_gradient.test(p, None)

    assert numpy.array_equal(qc, truth), 'failed to flag a gradient outside of delta temp and depth ranges, but inside gradshort ranges'     

    # temperature change too small
    p = util.testingProfile.fakeProfile([0,0.1], [0,0.2]) 
    qc = qctests.CSIRO_short_gradient.test(p, None)
    truth = numpy.zeros(2, dtype=bool)

    assert numpy.array_equal(qc, truth), 'flagged a gradient even though its temperature change was too small to consider' 