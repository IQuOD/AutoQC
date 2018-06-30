import qctests.AOML_spike
import util.testingProfile
import numpy

def test_AOML_spike():
    '''
    general behavior test for spike function
    '''

    assert qctests.AOML_spike.spike(numpy.ma.MaskedArray([1,2,3], [0,0,0])) == False, 'flagged an obviously smooth point'
    assert qctests.AOML_spike.spike(numpy.ma.MaskedArray([1,200,3], [0,0,0])), 'failed to flag an obvious spike'
    assert qctests.AOML_spike.spike(numpy.ma.MaskedArray([1,200,3],[0,0,1])) == False, 'failed to account for missing value correctly'
    assert qctests.AOML_spike.spike(numpy.ma.MaskedArray([1,-200,3], [0,0,0])), 'failed to flag an obvious negative spike'

def test_AOML_spike_slice():
    '''
    AOML_spike is supposed to consider a 3-level series at the boundaries of the profile,
    and a 5-level series everywhere else.
    '''

    p = util.testingProfile.fakeProfile([20,199,200,201,16],[1,2,3,4,5])
    qc = qctests.AOML_spike.test(p, None)
    truth = numpy.zeros(5, dtype=bool)
    truth[2] = True
    truth[3] = True
    assert numpy.array_equal(qc, truth), 'mishandled spikes on interior of profile'

    p = util.testingProfile.fakeProfile([20,190,18,18,18,170,16],[1,2,3,4,5,5,7])
    qc = qctests.AOML_spike.test(p, None)
    truth = numpy.zeros(7, dtype=bool)
    truth[1] = True
    truth[5] = True
    print qc
    print truth
    assert numpy.array_equal(qc, truth), 'failed to flag spikes near edges of profile'    