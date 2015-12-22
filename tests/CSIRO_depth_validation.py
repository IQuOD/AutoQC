import qctests.CSIRO_depth
import util.testingProfile
import numpy

##### CSIRO_depth_test ---------------------------------------------------

def test_CSIRO_depth():
    '''
    Spot-check the nominal behavior of the CSIRO depth test.
    '''

    # too shallow for an xbt
    p = util.testingProfile.fakeProfile([0,0,0], [0,1,20], probe_type=2) 
    qc = qctests.CSIRO_depth.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[0] = True
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failed to flag a too-shallow xbt measurement'

    # shallow but not an xbt - don't flag
    p = util.testingProfile.fakeProfile([0,0,0], [0,1,20], probe_type=1) 
    qc = qctests.CSIRO_depth.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a non-xbt measurement'    

    # threshold value - don't flag
    p = util.testingProfile.fakeProfile([0,0,0], [0,3.6,20], probe_type=2) 
    qc = qctests.CSIRO_depth.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[0] = True
    print qc
    assert numpy.array_equal(qc, truth), "shouldn't flag measurements at threshold"   