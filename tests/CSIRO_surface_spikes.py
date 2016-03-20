import qctests.CSIRO_surface_spikes
import util.testingProfile
import numpy

##### CSIRO_surface_spikes ---------------------------------------------------

def test_CSIRO_surface_spikes():
    '''
    Spot-check the nominal behavior of the CSIRO CSIRO_surface_spikes test.
    '''

    # nominal
    p = util.testingProfile.fakeProfile([0,0,0], [1,2,3], probe_type=2) 
    qc = qctests.CSIRO_surface_spikes.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[0] = True
    truth[1] = True

    assert numpy.array_equal(qc, truth), 'failed to flag a collection of shallow profiles' 

    # inappropriate probe type
    p = util.testingProfile.fakeProfile([0,0,0], [1,2,3], probe_type=1) 
    qc = qctests.CSIRO_surface_spikes.test(p)
    truth = numpy.zeros(3, dtype=bool)

    assert numpy.array_equal(qc, truth), 'flagged shallow profiles for an inappropriate probe type' 

    # no cluster
    p = util.testingProfile.fakeProfile([0,0,0], [1,20,30], probe_type=1) 
    qc = qctests.CSIRO_surface_spikes.test(p)
    truth = numpy.zeros(3, dtype=bool)

    assert numpy.array_equal(qc, truth), 'flagged shallow profile without a cluster' 