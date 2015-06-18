import qctests.Argo_pressure_increasing_test

import util.testingProfile
import numpy

##### Argo_pressure_increasing_test ---------------------------------------------------

def test_Argo_pressure_increasing_test_constantPressure():
    '''
    API test should flag only the subsequent levels of constant pressure.
    '''

    p = util.testingProfile.fakeProfile([2,2,2], [100,100,100]) 
    qc = qctests.Argo_pressure_increasing_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'must flag only subsequent levels of constant pressure.'    

def test_Argo_pressure_increasing_test_pressureInversion():
    '''
    API test should flag only the subsequent levels of constant pressure.
    '''

    p = util.testingProfile.fakeProfile([2,2,2], [100,200,100]) 
    qc = qctests.Argo_pressure_increasing_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'must flag all levels corresponding to pressure inversion.' 