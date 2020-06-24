import qctests.CSIRO_wire_break
import util.testingProfile
import numpy

##### CSIRO_wire_break_test ---------------------------------------------------

def test_CSIRO_wire_break():
    '''
    Spot-check the nominal behavior of the CSIRO wire break test.
    '''

    # too cold at the bottom of xbt profile
    p = util.testingProfile.fakeProfile([-2.399,-2.399,-2.4001], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'failed to flag too-cold temperature at bottom of profile'

    # too hot at bottom of xbt profile
    p = util.testingProfile.fakeProfile([31.99,31.99,32.001], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'failed to flag too-hot temperature at bottom of profile'

    # right on border - no flag
    p = util.testingProfile.fakeProfile([-2.399,-2.399,-2.4], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    print(qc)
    print(truth)
    assert numpy.array_equal(qc, truth), 'flagged marginally cold temperature at bottom of profile'

    p = util.testingProfile.fakeProfile([31.99,31.99,32], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged marginally hot temperature at bottom of profile'

    # don't flag if not an xbt
    p = util.testingProfile.fakeProfile([0,0,-100], [10,20,30], probe_type=1) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged non-xbt profile'

    # don't flag if not at bottom of profile
    p = util.testingProfile.fakeProfile([0,32.01,31.99], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), "flagged hot temperature that wasn't at bottom of profile"    

    # flag both sides of a gap
    p = util.testingProfile.fakeProfile([9,9,10], [10,20,30], probe_type=2) 
    qc = qctests.CSIRO_wire_break.test(p, None)
    truth = numpy.ones(3, dtype=bool)
    truth[0] = False
    assert numpy.array_equal(qc, truth), "should flag both sides of a gap"
