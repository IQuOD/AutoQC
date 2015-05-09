import qctests.Argo_global_range_check
import qctests.EN_range_check
import util.testingProfile
import numpy

def test_Argo_global_range_check_temperature():
    '''
    Make sure AGRC is flagging temperature excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([-2.500000001], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly colder than -2.5 C'

    # -2.5 OK
    p = util.testingProfile.fakeProfile([-2.5], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging -2.5 C'

    # 40 OK
    p = util.testingProfile.fakeProfile([40], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging 40 C'

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([40.0000001], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly warmer than 40 C'        



def test_EN_range_check_spotcheck():
    '''
    Spot-check the implementaion of EN_range_check.
    '''

    p = util.testingProfile.fakeProfile([1,1000,1], [100,200,300])

    qc = qctests.EN_range_check.test(p)

    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True

    assert numpy.array_equal(qc, truth)
