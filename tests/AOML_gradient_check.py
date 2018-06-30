import qctests.AOML_gradient

import util.testingProfile
import numpy
from util import obs_utils

def test_AOML_gradient_boundaries():
    '''
    Test critical values in AOML check
    unphysical giant numbers to avoid some floating point errors
    '''

    p = util.testingProfile.fakeProfile([500000,400000,299999], [100000,200000,300000]) 
    qc = qctests.AOML_gradient.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'incorrectly flagging boundaries of decreasing temperature gradient.'

    p = util.testingProfile.fakeProfile([480000,500000,520000], [100000,200000,299999]) 
    qc = qctests.AOML_gradient.test(p, None)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'incorrectly flagging boundaries of increasing temperature gradient.'    