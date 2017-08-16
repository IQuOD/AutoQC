import qctests.Argo_gradient_test
import util.testingProfile
import numpy

##### Argo_gradient_test ---------------------------------------------------

from util import obs_utils

def test_Argo_gradient_test_temperature_shallow():
    '''
    Make sure AGT is flagging postive and negative temperature spikes at shallow depths
    '''

    ###
    # shallow - depth < 500 m
    ###

    # pass a marginal positive spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,11,2], [100,200,300], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold (shallow).'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-7,2], [100,200,300], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold (shallow).' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,11.0001,2], [100,200,300], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold (shallow).'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-7.0001,2], [100,200,300], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
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
    p = util.testingProfile.fakeProfile([2,5,2], [1000,2000,3000], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold. (deep)'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-1,2], [1000,2000,3000], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold. (deep)' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,5.0001,2], [1000,2000,3000], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (deep)'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-1.0001,2], [1000,2000,3000], latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold. (deep)'

def test_Argo_gradient_test_temperature_threshold():
    ''' 
    check AGT temperature behavior exactly at depth threshold (500m)
    '''
    # middle value should fail the deep check but pass the shallow check;
    # at threshold, use deep criteria
    p = util.testingProfile.fakeProfile([2,5.0001,2], obs_utils.pressure_to_depth([400,500,600], 0.0), latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (threshold)'      

    # as above, but passes just above 500m
    p = util.testingProfile.fakeProfile([2,5.0001,2], obs_utils.pressure_to_depth([400,499,600], 0.0), latitude=0.0) 
    qc = qctests.Argo_gradient_test.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a spike using deep criteria when shallow should have been used. (threshold)' 
