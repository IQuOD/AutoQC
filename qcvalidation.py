import qctests.Argo_global_range_check
import qctests.Argo_gradient_test
import qctests.EN_range_check
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

##### Argo_gradient_test ---------------------------------------------------

def test_Argo_gradient_test_temperature_shallow():
    '''
    Make sure AGT is flagging postive and negative temperature spikes at shallow depths
    '''

    ###
    # shallow - depth < 500 m
    ###

    # pass a marginal positive spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,11,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold (shallow).'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-7,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold (shallow).' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,11.0001,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold (shallow).'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-7.0001,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold (shallow).'

def test_Argo_gradient_test_temperature_deep():
    '''
    Make sure AGT is flagging postive and negative temperature spikes at deep depths
    '''

    ###
    # deep - depth > 500 m
    ###

    # pass a marginal positive spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,5,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold. (deep)'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-1,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold. (deep)' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,5.0001,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (deep)'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-1.0001,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold. (deep)'

def test_Argo_gradient_test_temperature_threshold():
    '''
    check AGT temperature behavior exactly at depth threshold (500m)
    '''
    # middle value should fail the deep check but pass the shallow check;
    # at threshold, use deep criteria
    p = util.testingProfile.fakeProfile([2,5.0001,2], [400,500,600]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (threshold)'      

    # as above, but passes just above 500m
    p = util.testingProfile.fakeProfile([2,5.0001,2], [400,499,600]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a spike using deep criteria when shallow should have been used. (threshold)' 

def test_Argo_gradient_test_temperature_floatingPoint():
    '''
    check AGT temperature check for floating point errors
    '''

    #should just barely pass, but bad fp can push it over the threshold
    p = util.testingProfile.fakeProfile([8.1, 11.15, 8.2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'floating point error'

##### EN_range_check ---------------------------------------------------

def test_EN_range_check_spotcheck():
    '''
    Spot-check the implementaion of EN_range_check.
    '''

    p = util.testingProfile.fakeProfile([1,1000,1], [100,200,300])

    qc = qctests.EN_range_check.test(p)

    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True

    assert numpy.array_equal(qc, truth)
