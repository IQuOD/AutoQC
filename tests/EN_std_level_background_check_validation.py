import qctests.EN_std_lev_bkg_and_buddy_check
import qctests.EN_background_check
import qctests.EN_spike_and_step_check
from cotede.qctests.possible_speed import haversine
from util import main
import util.testingProfile
import numpy, pickle, StringIO

# Dummy functions to turn off functions that do not
# work on a testing profile.
def dummycatchflagsfunc(arg): 
    pass
realcatchflagsfunc = main.catchFlags
realgetproffunc    = main.get_profile_from_db

def profile_to_info_list(p):
    '''
    fake a query response for a profile p
    '''
    return (p.uid(),p.year(),p.month(),p.cruise(),p.latitude(),p.longitude())

def dummy_get_profile_from_db(uid):
    if uid == 1:
        return realProfile1
    elif uid == 2:
        return realProfile2
    elif uid == 3:
        return realProfile3
    else:
        return util.testingProfile.fakeProfile([0,0,0],[0,0,0],date=[1999,12,31,23.99], latitude=0, longitude=0,cruise=1234, uid=uid)

##### EN_std_lev_bkg_and_buddy_check ---------------------------------------------------

class TestClass():

    parameters = {
        "table": 'unit'
    }
    qctests.EN_background_check.loadParameters(parameters)

    def setUp(self):
        # this qc test will go looking for the profile in question in the db, needs to find something sensible
        main.faketable('unit')
        main.fakerow('unit')
        main.catchFlags = dummycatchflagsfunc
        main.get_profile_from_db = dummy_get_profile_from_db
        # need to re-do this every time to refresh the enspikeandstep table
        qctests.EN_spike_and_step_check.loadParameters(self.parameters)

    def tearDown(self):
        main.dbinteract('DROP TABLE unit;')
        main.catchFlags = realcatchflagsfunc
        main.get_profile_from_db = realgetproffunc

    def test_EN_std_level_bkg_and_buddy_check_temperature(self):
        '''
        Make sure EN_std_level_background_check is flagging temperature excursions
        '''

        p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7, uid=8888) 
        qc = qctests.EN_std_lev_bkg_and_buddy_check.test(p, self.parameters)
        expected = [False, False, False, False]
        assert numpy.array_equal(qc, expected), 'mismatch between qc results and expected values'

    def test_determine_pge(self):
        '''
        totally ridiculous differences between observation and background should give pge == 1
        '''

        p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 01, 15, 0], probe_type=7, uid=8888) 
        levels = numpy.ma.array([1000,1000,1000,1000])
        levels.mask = False

        #bgev = qctests.EN_background_check.bgevStdLevels
        qctests.EN_background_check.test(p, self.parameters) #need to populate the enbackground db with profile specific info
        query = 'SELECT bgevstdlevels FROM enbackground WHERE uid = 8888'
        enbackground_pars = main.dbinteract(query) 
        bgev = pickle.load(StringIO.StringIO(enbackground_pars[0][0]))

        obev = self.parameters['enbackground']['obev']
        expected = [1.0, 1.0, 1.0, 1.0]
        assert numpy.array_equal(qctests.EN_std_lev_bkg_and_buddy_check.determine_pge(levels, bgev, obev, p), expected), 'PGE of extreme departures from background not flagged as 1.0'

    def test_buddyCovariance_time(self):
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

    def test_buddyCovariance_mesoscale(self):
        '''
        make sure buddyCovariance displays the correct behavior in mesoscale correlation.
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 6, 12])
        buddyCovariance_100km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100000, p1, p2, 1, 1, 0, 0)
        buddyCovariance_200km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(200000, p1, p2, 1, 1, 0, 0)
      

        assert buddyCovariance_100km * numpy.exp(-1) - buddyCovariance_200km < 1e-12, 'incorrect mesoscale correlation'

    def test_buddyCovariance_synoptic_scale(self):
        '''
        make sure buddyCovariance displays the correct behavior in synoptic scale correlation.
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 6, 12])
        buddyCovariance_100km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(100000, p1, p2, 0, 0, 1, 1)
        buddyCovariance_500km = qctests.EN_std_lev_bkg_and_buddy_check.buddyCovariance(500000, p1, p2, 0, 0, 1, 1)
      
        assert buddyCovariance_100km * numpy.exp(-1) - buddyCovariance_500km < 1e-12, 'incorrect synoptic scale correlation'

    def test_filterLevels(self):
        '''
        check that filterLevels removes the expected elements from its arguments.
        '''

        preQC = [True, False, True, True, False]
        origLevels = numpy.array([0,2,3,4])
        diffLevels = numpy.array([10,11,12,13])

        nLevels, origLevels, diffLevels = qctests.EN_std_lev_bkg_and_buddy_check.filterLevels(preQC, origLevels, diffLevels)

        assert numpy.array_equal(origLevels, [4])
        assert numpy.array_equal(diffLevels, [13])

    def test_meanDifferencesAtStandardLevels(self):
        '''
        check a simple case for calculating mean level differences.
        '''

        stdLevels = self.parameters['enbackground']['depth']

        origLevels = [0,2,3]
        diffLevels = [3,5,7]
        depths = [5, 5.1, 45, 46]

        levels, assocLevs = qctests.EN_std_lev_bkg_and_buddy_check.meanDifferencesAtStandardLevels(origLevels, diffLevels, depths, self.parameters)

        trueLevels = numpy.zeros(len(stdLevels))
        trueLevels[0] = 3 # level 0 alone
        trueLevels[4] = 6 # level 2 and 3 averaged
        trueLevels = numpy.ma.array(trueLevels)
        trueLevels.mask = False

        assert numpy.array_equal(levels, trueLevels)
        assert numpy.array_equal(assocLevs, [0,4,4]) # since 5 ~ first standard level, 5.1 isn't considered, and 45 and 46 are ~ 5th std. level.

    def test_assessBuddyDistance_invalid_buddies(self):
        '''
        check buddy distance rejects invalid buddy pairs
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 13], uid=0, cruise=2)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) is None, 'accepted buddies with same uid'

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1901, 1, 1, 13], uid=1, cruise=2)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) is None, 'accepted buddies with different year'

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 2, 1, 13], uid=1, cruise=2)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) is None, 'accepted buddies with different month'

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 13], uid=1, cruise=1)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) is None, 'accepted buddies with same cruise'

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 5.01, 0, date=[1900, 1, 1, 13], uid=1, cruise=2)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) is None, 'accepted buddies too far apart in latitude'

    def test_assessBuddyDistance_haversine(self):
        '''
        make sure haversine calculation is consistent with rest of package
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 0, 0, date=[1900, 1, 1, 12], uid=0, cruise=1)
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], 1, 1, date=[1900, 1, 1, 13], uid=1, cruise=2)
        assert qctests.EN_std_lev_bkg_and_buddy_check.assessBuddyDistance(p1, profile_to_info_list(p2)) == haversine(0,0,1,1), 'haversine calculation inconsistent with cotede.qctests.possible_speed.haversine'


    def test_timeDiff(self):
        '''
        standard behavior of time difference calculator
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 12])
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 13])

        assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p1, p2) == 3600, 'incorrect time difference reported'
        assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p2, p1) == 3600, 'time differences should always be positive'

    def test_timeDiff_garbage_time(self):
        '''
        timeDiff returns none when it finds garbage times
        '''

        p1 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, -1, 1, 12])
        p2 = util.testingProfile.fakeProfile([0,0,0],[0,0,0], date=[1900, 1, 1, 13])

        assert qctests.EN_std_lev_bkg_and_buddy_check.timeDiff(p1, p2) is None, 'failed to reurn None when a nonsesne date was found'

    def test_EN_std_level_bkg_and_buddy_real_profiles_1(self):
        '''
        Make sure EN_std_level_background_check is flagging temperature excursions
        '''

        main.fakerow('unit', raw='x', truth=0, uid=1, year=2000, month=1, day=15, time=12, lat=-39.889, longitude=17.650000, cruise=1, probe=2)
        qc = qctests.EN_std_lev_bkg_and_buddy_check.test(realProfile1, self.parameters)

        assert numpy.array_equal(qc, truthQC1), 'mismatch between qc results and expected values'

    def test_EN_std_level_bkg_and_buddy_real_profiles_2(self):
        '''
        Make sure EN_std_level_background_check is flagging temperature excursions
        '''

        main.fakerow('unit', raw='x', truth=0, uid=2, year=2000, month=1, day=10, time=0, lat=-30.229, longitude=2.658, cruise=2, probe=2)
        main.fakerow('unit', raw='x', truth=0, uid=3, year=2000, month=1, day=10, time=0.1895833, lat=-28.36, longitude=-0.752, cruise=3, probe=2)
        qc = qctests.EN_std_lev_bkg_and_buddy_check.test(realProfile2, self.parameters, allow_level_reinstating=False)

        assert numpy.array_equal(qc, truthQC2), 'mismatch between qc results and expected values'

    def test_EN_std_level_bkg_and_buddy_real_profiles_3(self):
        '''
        Make sure EN_std_level_background_check is flagging temperature excursions - ensure that level reinstating is working.
        '''

        main.fakerow('unit', raw='x', truth=0, uid=2, year=2000, month=1, day=10, time=0, lat=-30.229, longitude=2.658, cruise=2, probe=2)
        main.fakerow('unit', raw='x', truth=0, uid=3, year=2000, month=1, day=10, time=0.1895833, lat=-28.36, longitude=-0.752, cruise=3, probe=2)
        qc = qctests.EN_std_lev_bkg_and_buddy_check.test(realProfile2, self.parameters)
        assert numpy.all(qc == False), 'mismatch between qc results and expected values'

realProfile1 = util.testingProfile.fakeProfile(
                [20.6900,      20.6900,      20.6900,      20.6900,
                 20.6900,      20.6900,      20.6900,      20.6900,
                 20.6900,      20.6600,      20.4300,      19.9100,
                 19.6600,      19.5300,      19.3000,      19.2200,
                 19.1300,      19.0400,      18.9600,      18.8200,
                 18.7400,      18.4300,      18.0900,      17.6900,
                 17.2300,      16.8300,      16.4200,      15.9900, 
                 15.4600,      14.9400,      14.6400,      14.1800,
                 13.7500,      13.2200,      12.7000,      12.0100,
                 11.3000,      10.6400,      10.0000,      9.36000,
                 8.66000,      8.37000,      7.58000,      6.86000,
                 5.46000,      5.03000,      4.79000,      4.42000,
                 4.10000,      3.66000,      3.53000,      3.42000,
                 3.17000,      3.05000,      3.02000,      2.93000],
                [5.00000,      9.00000,      15.0000,      21.0000,
                 27.0000,      33.0000,      39.0000,      45.0000,   
                 51.0000,      57.0000,      63.0000,      68.0000,
                 74.0000,      80.0000,      86.0000,      92.0000,  
                 98.0000,      104.000,      110.000,      116.000,
                 122.000,      140.000,      170.000,      199.000,
                 229.000,      259.000,      289.000,      318.000,
                 348.000,      378.000,      407.000,      437.000,
                 467.000,      511.000,      571.000,      630.000,
                 690.000,      749.000,      808.000,      867.000,
                 927.000,      986.000,      1045.00,      1104.00,
                 1164.00,      1223.00,      1282.00,      1341.00,
                 1400.00,      1460.00,      1519.00,      1578.00,
                 1637.00,      1696.00,      1755.00,      1814.00],
                date=[2000, 1, 15, 12], latitude=-39.889, longitude=17.650000,
                cruise=1, uid=1)

truthQC1=numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
                      1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=bool)

realProfile2 = util.testingProfile.fakeProfile(
                [21.4200,      21.1300,      20.4800,      19.8400,
                 19.2000,      18.9400,      18.7600,      18.5000, 
                 18.0700,      17.5900,      17.3400,      17.0000,
                 16.8000,      16.6200,      16.5700,      16.4900,
                 16.4500,      16.4100,      16.3900,      16.3500,
                 16.3300,      16.3300,      16.3300,      16.3200,
                 16.3000,      16.2800,      16.2700,      16.2400,
                 16.2300,      16.2100,      16.2000,      16.1700, 
                 16.1400,      16.1100,      16.0800,      16.0500,
                 16.0200,      15.9900,      15.9700,      15.9400, 
                 15.7500,      15.6000,      15.3700,      14.9300,
                 14.7200,      14.4800,      14.1600,      13.8000,
                 13.6600,      13.3100,      12.4700,      11.7400,
                 10.9700,      10.4300,      9.69000,      8.42000,
                 7.20000,      6.22000,      5.48000,      5.02000,
                 4.59000,      4.18000,      4.05000,      4.01000],
                [5.00000,      10.0000,      15.0000,      20.0000,
                 25.0000,      30.0000,      35.0000,      40.0000,
                 45.0000,      50.0000,      55.0000,      60.0000,
                 65.0000,      70.0000,      74.0000,      79.0000, 
                 84.0000,      89.0000,      94.0000,      99.0000, 
                 104.000,      109.000,      114.000,      119.000,
                 124.000,      129.000,      134.000,      139.000,
                 144.000,      149.000,      154.000,      159.000,
                 164.000,      169.000,      174.000,      179.000,
                 184.000,      189.000,      194.000,      199.000,
                 218.000,      238.000,      258.000,      278.000,
                 298.000,      318.000,      337.000,      357.000,
                 377.000,      397.000,      446.000,      496.000,  
                 546.000,      595.000,      645.000,      694.000,
                 744.000,      793.000,      842.000,      892.000,
                 941.000,      991.000,      1040.00,      1068.00],
               date=[2000,1,10,0], latitude=-30.229, longitude=2.658,
               cruise=2, uid=2)

truthQC2 = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                       dtype=bool)

realProfile3 = util.testingProfile.fakeProfile(
                [22.9400,      21.8800,      21.1200,      20.6100,
                 20.3600,      19.5500,      19.1200,      18.5600,
                 17.9400,      17.6900,      17.4800,      17.2600,
                 17.1000,      16.9000,      16.7400,      16.5800, 
                 16.4200,      16.2900,      16.1900,      16.0700,
                 15.9200,      15.3700,      14.5000,      13.8400,
                 13.2600,      12.8200,      12.3100,      11.9200,
                 11.4300,      10.9800,      10.4100,      9.77000, 
                 8.75000,      7.66000,      6.77000,      5.91000,
                 5.14000,      4.63000,      4.25000,      4.00000, 
                 3.75000,      3.61000,      3.46000,      3.34000, 
                 3.24000,      3.21000,      3.21000,      3.21000,
                 3.18000,      3.12000,      3.08000,      3.06000, 
                 3.04000,      3.02000,      2.97000,      2.88000],
                [5.00000,      9.00000,      15.0000,      21.0000,
                 27.0000,      33.0000,      39.0000,      45.0000,
                 51.0000,      57.0000,      63.0000,      69.0000,
                 74.0000,      80.0000,      86.0000,      92.0000,
                 98.0000,      104.000,      110.000,      116.000,
                 122.000,      140.000,      170.000,      200.000,
                 229.000,      259.000,      289.000,      319.000,
                 348.000,      378.000,      408.000,      438.000,
                 482.000,      542.000,      601.000,      660.000,
                 720.000,      779.000,      839.000,      898.000,
                 957.000,      1017.00,      1076.00,      1135.00,
                 1194.00,      1254.00,      1313.00,      1372.00,
                 1431.00,      1491.00,      1550.00,      1609.00,
                 1668.00,      1727.00,      1786.00,      1845.00],
                date=[2000,1,10,0.1895833], latitude=-28.36, longitude=-0.752,
                cruise=3, uid=3)


