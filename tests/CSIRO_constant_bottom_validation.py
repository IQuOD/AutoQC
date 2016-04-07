import qctests.CSIRO_constant_bottom
import util.testingProfile
import numpy

##### CSIRO_constant_bottom ---------------------------------------------------

def test_CSIRO_constant_bottom():
    '''
    Spot-check the nominal behavior of the CSIRO constant bottom test.
    '''

    # nominal
    p = util.testingProfile.fakeProfile([0,0,0], [0,100,200], latitude=0, longitude=0, probe_type=2) 
    qc = qctests.CSIRO_constant_bottom.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = True

    assert numpy.array_equal(qc, truth), 'failed to flag a constant temperature at bottom of profile' 

    # inappropriate probe type
    p = util.testingProfile.fakeProfile([0,0,0], [0,100,200], latitude=0, longitude=0, probe_type=1) 
    qc = qctests.CSIRO_constant_bottom.test(p)
    truth = numpy.zeros(3, dtype=bool)

    assert numpy.array_equal(qc, truth), 'flagged a constant temperature for an inappropriate probe type' 

    # inappropriate latitude
    p = util.testingProfile.fakeProfile([0,0,0], [0,100,200], latitude=-41, longitude=0, probe_type=2) 
    qc = qctests.CSIRO_constant_bottom.test(p)

    assert numpy.array_equal(qc, truth), 'flagged a constant temperature for an inappropriate latitude' 

    # inappropriate depth difference
    p = util.testingProfile.fakeProfile([0,0,0], [0,100,100], latitude=0, longitude=0, probe_type=2) 
    qc = qctests.CSIRO_constant_bottom.test(p)

    assert numpy.array_equal(qc, truth), 'flagged a constant temperature for an inappropriate depth distance'

    # not at bottom of profile
    p = util.testingProfile.fakeProfile([0,0, -1], [100,200,300], latitude=0, longitude=0, probe_type=2) 
    qc = qctests.CSIRO_constant_bottom.test(p)

    assert numpy.array_equal(qc, truth), 'flagged a constant temperature not at the bottom of the profile'