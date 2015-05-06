import qctests.EN_range_check
import util.testingProfile
import numpy

def test_EN_range_check_spotcheck():
    '''
    Spot-check the implementaion of EN_range_check.
    '''

    p = util.testingProfile.fakeProfile([1,1000,1], [100,200,300])

    qc = qctests.EN_range_check.test(p)

    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True

    assert numpy.array_equal(qc, truth)
