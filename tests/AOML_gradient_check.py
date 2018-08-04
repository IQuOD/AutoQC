import qctests.AOML_gradient
import util.testingProfile
import numpy

def test_AOML_gradient_boundaries():
    '''
    Test critical values in AOML check
    unphysical giant numbers to avoid some floating point errors
    '''

    p = util.testingProfile.fakeProfile([500000,400000,299999], [100000,200000,300000]) 
    qc = qctests.AOML_gradient.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'incorrectly flagging boundaries of decreasing temperature gradient.'

    p = util.testingProfile.fakeProfile([480000,500000,520000], [100000,200000,299999]) 
    qc = qctests.AOML_gradient.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'incorrectly flagging boundaries of increasing temperature gradient.'

def test_AOML_gradient_edge():
    '''
    check the edge case pointed out in
    https://github.com/IQuOD/AutoQC/pull/228
    '''

    p = util.testingProfile.fakeProfile([1.8,1], [2,1]) 
    qc = qctests.AOML_gradient.test(p, None)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a moderate gradient even though temperature was decreasing'