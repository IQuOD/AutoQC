import qctests.AOML_constant
import util.testingProfile
import numpy

def test_AOML_constant():
    '''
    Test basic behavior of AOML_constant
    '''

    p = util.testingProfile.fakeProfile([0,0,0], [0, 1, 2]) 
    qc = qctests.AOML_constant.test(p, None)
    truth = numpy.ones(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failed to flag constant temperature'

    t = numpy.ma.MaskedArray([1,2,1], [0,1,0])
    p = util.testingProfile.fakeProfile(t, [0, 1, 2]) 
    qc = qctests.AOML_constant.test(p, None)
    truth = numpy.ones(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failed to ignore masked value correctly'

    p = util.testingProfile.fakeProfile([0], [0]) 
    qc = qctests.AOML_constant.test(p, None)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged single level profile'

    t = numpy.ma.MaskedArray([1,1], [0,1])
    p = util.testingProfile.fakeProfile(t, [0, 1]) 
    qc = qctests.AOML_constant.test(p, None)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged profile with only a single unmasked level'