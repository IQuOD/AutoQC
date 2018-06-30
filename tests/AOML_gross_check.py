import qctests.AOML_gross
import util.testingProfile
import numpy

def test_AOML_gross():
    '''
    Test critical values in AOML check
    '''

    p = util.testingProfile.fakeProfile([40.0000001, 40, 30, 20, 10, 0, -2.5, -2.5000001], [0, 10, -10, 20, 3000, 40, 50, 60]) 
    qc = qctests.AOML_gross.test(p, None)
    truth = numpy.zeros(8, dtype=bool)
    truth[0] = True
    truth[2] = True
    truth[4] = True
    truth[7] = True
    assert numpy.array_equal(qc, truth), 'incorrectly temperature and depth ranges.'