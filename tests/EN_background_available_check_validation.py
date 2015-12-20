import qctests.EN_background_available_check
from util import main
import util.testingProfile
import numpy

##### EN_background_check ---------------------------------------------------

def test_EN_background_available_check_depth():
    '''
    Make sure EN_background_check is flagging depths where the background is not defined.
    '''

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 1.8], [0.0, 2.5, 5.0, 5600.0], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7) 
    qc = qctests.EN_background_available_check.test(p)
    expected = [False, False, False, True]
    assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'

def test_EN_background_available_check_location():
    '''
    Make sure EN_background_check is flagging land locations.
    '''

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 1.8], [0.0, 2.5, 5.0, 7.5], latitude=0.0, longitude=20.0, date=[1900, 01, 15, 0], probe_type=7) 
    qc = qctests.EN_background_available_check.test(p)
    expected = [True, True, True, True]
    assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'


