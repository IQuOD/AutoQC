import qctests.CSIRO_long_gradient
import util.testingProfile
import numpy

##### CSIRO_long_gradient ---------------------------------------------------

def test_CSIRO_long_gradient():
    '''
    Spot-check the nominal behavior of the CSIRO long gradient test.
    '''

    # nominal
    p = util.testingProfile.fakeProfile([20,10,15,15,15,10], [0,5,10,15,20,25]) 
    qc = qctests.CSIRO_long_gradient.test(p, None)
    truth = numpy.zeros(6, dtype=bool)
    truth[1] = True

    assert numpy.array_equal(qc, truth), 'failed to flag a nominal long inversion'

    # gradlong too large
    p = util.testingProfile.fakeProfile([20,10,15,15,15,10], [0,10,20,30,40,50]) 
    qc = qctests.CSIRO_long_gradient.test(p, None)
    truth = numpy.zeros(6, dtype=bool)

    assert numpy.array_equal(qc, truth), 'should not flag a long inversion with such a large gradient'   

    # too shallow
    p = util.testingProfile.fakeProfile([20,10,15,15,15,10], [0,1,6,11,16,21]) 
    qc = qctests.CSIRO_long_gradient.test(p, None)
    truth = numpy.zeros(6, dtype=bool)

    print truth, qc

    assert numpy.array_equal(qc, truth), 'should not flag a long inversion that begins at < 5m' 