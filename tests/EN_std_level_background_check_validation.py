import qctests.EN_std_lev_background_check
from util import main
import util.testingProfile
import numpy

##### EN_background_check ---------------------------------------------------

def test_EN_background_check_temperature():
    '''
    Make sure EN_std_level_background_check is flagging temperature excursions
    '''

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7) 
    qc = qctests.EN_std_lev_background_check.test(p)
    expected = [False, False, False, False]
    print qc
    assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'


