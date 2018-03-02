import qctests.CSIRO_wire_break
import util.testingProfile
import numpy

##### CSIRO_wire_break_test ---------------------------------------------------

def test_CSIRO_wire_break():
    '''
    Spot-check the nominal behavior of the CSIRO wire break test.
    '''
   
    # bottom level tests

    # too cold at the bottom of xbt profile
    p = util.testingProfile.fakeProfile([0,0,-20], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'failed to flag too-cold temperature at bottom of profile'

    # too hot at bottom of xbt profile
    p = util.testingProfile.fakeProfile([0,0,100], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'failed to flag too-hot temperature at bottom of profile'

    # right on border - no flag
    p = util.testingProfile.fakeProfile([0,0,-2.8], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = False
    assert numpy.array_equal(qc, truth), 'flagged marginally cold temperature at bottom of profile'

    p = util.testingProfile.fakeProfile([0,0,36], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = False
    assert numpy.array_equal(qc, truth), 'flagged marginally hot temperature at bottom of profile'

    # don't flag if not an xbt
    p = util.testingProfile.fakeProfile([0,0,-100], [10,20,30], probe_type=1) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = False
    assert numpy.array_equal(qc, truth), 'flagged non-xbt profile'

    # don't flag if not at bottom of profile
    p = util.testingProfile.fakeProfile([0,-100,0], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = False
    assert numpy.array_equal(qc, truth), "flagged cold temperature that wasn't at bottom of profile"   

    # transition tests 

    p = util.testingProfile.fakeProfile([10,10,20,50,50], [1,2,3,4,5], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.asarray([False, False, True, True, True])
    assert numpy.array_equal(qc, truth), "misflagged gradient (warm)"

    p = util.testingProfile.fakeProfile([10,10,-20,-50,-50], [1,2,3,4,5], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.asarray([False, False, True, True, True])
    assert numpy.array_equal(qc, truth), "misflagged gradient (cold)"

    p = util.testingProfile.fakeProfile([10,10,20,30,30], [1,2,3,4,5], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = truth = numpy.zeros(5, dtype=bool)
    assert numpy.array_equal(qc, truth), "flagged gradient when final level didn't look like a wire break"         