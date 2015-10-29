import qctests.EN_stability_check

import util.testingProfile
import numpy

##### EN_stability_check ----------------------------------------------

def test_mcdougallEOS():
    '''
    check the test values provided in McDougall 2003
    '''

    eos = round(qctests.EN_stability_check.mcdougallEOS(35,25,2000), 6)
    assert  eos == 1031.654229, 'mcdougallEOS(35,25,2000) should be 1031.654229, instead got %f' % eos
    eos = round(qctests.EN_stability_check.mcdougallEOS(20,20,1000), 6)
    assert  eos == 1017.726743, 'mcdougallEOS(20,20,1000) should be 1017.726743, instead got %f' % eos
    eos = round(qctests.EN_stability_check.mcdougallEOS(40,12,8000), 6)
    assert  eos == 1062.928258, 'mcdougallEOS(40,12,8000) should be 1062.928258, instead got %f' % eos