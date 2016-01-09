import qctests.EN_std_lev_bkg_and_buddy_check
import qctests.EN_background_check
from cotede.qctests.possible_speed import haversine
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

def test_timeDiff_garbage_time():
    '''
    timeDiff returns none when it finds garbage times
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, -1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 13])

    assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p1, p2) is None, 'failed to reurn None when a nonsesne date was found'

def test_assessBuddyDistance_invalid_buddies():
    '''
    check buddy distance rejects invalid buddy pairs
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 13], uid=0, cruise=2)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) is None, 'accepted buddies with same uid'

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1901, 1, 1, 13], uid=1, cruise=2)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) is None, 'accepted buddies with different year'

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 2, 1, 13], uid=1, cruise=2)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) is None, 'accepted buddies with different month'

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 13], uid=1, cruise=1)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) is None, 'accepted buddies with same cruise'

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 5.01, 0, date=[1900, 1, 1, 13], uid=1, cruise=2)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) is None, 'accepted buddies too far apart in latitude'

def test_assessBuddyDistance_haversine():
    '''
    make sure haversine calculation is consistent with rest of package
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 1, 1, date=[1900, 1, 1, 13], uid=1, cruise=2)
    assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, p2) == haversine(0,0,1,1), 'haversine calculation inconsistent with cotede.qctests.possible_speed.haversine'


def test_buddyCovariance_time():
    '''
    make sure buddyCovariance displays the correct behavior in time.
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 6, 12])
    buddyCovariance_5days = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100, p1, p2, 1, 1, 1, 1)

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 11, 12])
    buddyCovariance_10days = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100, p1, p2, 1, 1, 1, 1)    

    assert buddyCovariance_5days * numpy.exp(-3) - buddyCovariance_10days < 1e-12, 'incorrect timescale behavior'

def test_buddyCovariance_mesoscale():
    '''
    make sure buddyCovariance displays the correct behavior in mesoscale correlation.
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 6, 12])
    buddyCovariance_100km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100000, p1, p2, 1, 1, 0, 0)
    buddyCovariance_200km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(200000, p1, p2, 1, 1, 0, 0)
  

    assert buddyCovariance_100km * numpy.exp(-1) - buddyCovariance_200km < 1e-12, 'incorrect mesoscale correlation'

def test_buddyCovariance_synoptic_scale():
    '''
    make sure buddyCovariance displays the correct behavior in synoptic scale correlation.
    '''

    p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
    p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 6, 12])
    buddyCovariance_100km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100000, p1, p2, 0, 0, 1, 1)
    buddyCovariance_500km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(500000, p1, p2, 0, 0, 1, 1)
  
    assert buddyCovariance_100km * numpy.exp(-1) - buddyCovariance_500km < 1e-12, 'incorrect synoptic scale correlation'
