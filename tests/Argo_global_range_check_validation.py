import qctests.Argo_global_range_check
import util.testingProfile
import numpy

##### Argo_global_range_check ---------------------------------------------------

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

def test_Argo_global_range_check_pressure():
    '''
    Make sure AGRC is flagging pressure excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([5], [-5.00000001]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag pressure slightly below -5 '

    # -5 OK
    p = util.testingProfile.fakeProfile([5], [-5]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging pressure of -5'