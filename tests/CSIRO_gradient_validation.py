import qctests.CSIRO_gradient
import util.testingProfile
import numpy

##### CSIRO_gradient_test ---------------------------------------------------

def test_CSIRO_gradient():
    '''
    Spot-check some values in the CSIRO gradient test.
    '''

    p = util.testingProfile.fakeProfile([0,10,0,0.1,-24.9,-24.1], [10,20,30,40,50,60]) 
    qc = qctests.CSIRO_gradient.test(p)
    truth = numpy.zeros(6, dtype=bool)
    truth[0] = True;  # in range
    truth[1] = False; # too low
    truth[2] = False; # too high
    truth[3] = False; # right on the low margin
    truth[4] = False; # right on the high margin
    truth[5] = False; # can't caluclate gradient at endpoint

    assert numpy.array_equal(qc, truth), 'nominal beahvior failure in CSIRO_gradient'