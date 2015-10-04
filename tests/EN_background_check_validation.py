import qctests.EN_background_check
from util import main

import util.testingProfile
import numpy

##### EN_range_check ---------------------------------------------------

def test_EN_background_check_temperature():
    '''
    Make sure EN_background_check is flagging temperature excursions
    '''

    kwargs = {}
    main.readENBackgroundCheckAux(['EN_background_check'], kwargs)

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7) 
    qc = qctests.EN_background_check.test(p, **kwargs)
    expected = [False, False, False, True]
    assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'
        

