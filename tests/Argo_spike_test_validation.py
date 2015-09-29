import qctests.Argo_spike_test

import util.testingProfile
import numpy

##### Argo_spike_test ---------------------------------------------------

def test_Argo_spike_test_temperature_shallow():
    '''
    Make sure AST is flagging postive and negative temperature spikes at shallow depths
    '''

    ###
    # shallow - depth < 500 m
    ###

    # pass a marginal positive spike (criteria exactly 6 C):
    p = util.testingProfile.fakeProfile([5,11,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold (shallow).'    

    # pass a marginal negative spike (criteria exactly 6 C):
    p = util.testingProfile.fakeProfile([5,-1,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold (shallow).' 

    # fail a marginal positive spike (criteria > 6 C):
    p = util.testingProfile.fakeProfile([5,11.0001,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold (shallow).'    

    # fail a marginal negative spike (criteria > 6 C):
    p = util.testingProfile.fakeProfile([5,-1.0001,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold (shallow).'

def test_Argo_spike_test_temperature_deep():
    '''
    Make sure AST is flagging postive and negative temperature spikes at deep depths
    '''

    ###
    # deep - depth > 500 m
    ###

    # pass a marginal positive spike (criteria exactly 2 C):
    p = util.testingProfile.fakeProfile([5,7,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold. (deep)'    

    # pass a marginal negative spike (criteria exactly 2 C):
    p = util.testingProfile.fakeProfile([5,3,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold. (deep)' 

    # fail a marginal positive spike (criteria > 2 C):
    p = util.testingProfile.fakeProfile([5,7.0001,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (deep)'    

    # fail a marginal negative spike (criteria > 2 C):
    p = util.testingProfile.fakeProfile([5,2.999,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold. (deep)'

def test_Argo_spike_test_temperature_threshold():
    '''
    check AST temperature behavior exactly at depth threshold (500m)
    '''
    # middle value should fail the deep check but pass the shallow check;
    # at threshold, use deep criteria
    p = util.testingProfile.fakeProfile([5,7.0001,5], [400,500,600]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (threshold)'      

    # as above, but passes just above 500m
    p = util.testingProfile.fakeProfile([5,7.0001,5], [400,499,600]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a spike using deep criteria when shallow should have been used. (threshold)' 