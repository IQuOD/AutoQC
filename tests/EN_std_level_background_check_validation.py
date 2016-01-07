import qctests.EN_std_lev_bkg_and_buddy_check
import qctests.EN_background_check
from util import main
import util.testingProfile
import numpy
import __main__

##### EN_std_lev_bkg_and_buddy_check ---------------------------------------------------

def test_EN_std_level_bkg_and_buddy_check_temperature():
    '''
    Make sure EN_std_level_background_check is flagging temperature excursions
    '''

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7) 
    __main__.profiles = [p]
    qc = qctests.EN_std_lev_bkg_and_buddy_check.test(p)
    expected = [False, False, False, False]
    print qc
    assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'

def test_determine_pge():
    '''
    totally ridiculous differences between observation and background should give pge == 1
    '''

    p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7) 
    levels = numpy.ma.array([1000,1000,1000,1000])
    levels.mask = False
    bgev = qctests.EN_background_check.bgevStdLevels
    obev = qctests.EN_background_check.auxParam['obev']
    expected = [1.0, 1.0, 1.0, 1.0]
    assert numpy.array_equal(qctests.EN_std_lev_bkg_and_buddy_check.determine_pge(levels, bgev, obev, p), expected), 'PGE of extreme departures from background not flagged as 1.0'

def test_timeDiff():
    '''
    standard behavior of time difference calculator
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 13])

    assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p1, p2) == 3600, 'incorrect time difference reported'
    assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p2, p1) == 3600, 'time differences should always be positive'