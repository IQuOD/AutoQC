import util.main as main
import os, math
from wodpy import wod
import numpy, pandas
import util.testingProfile
import qctests.EN_track_check
import util.geo
import data.ds as ds

class TestClass():
    distRes = 20000. #meters
    timeRes = 600.   #seconds

    def setUp(self):
        qctests.EN_track_check.EN_track_results = {}
        qctests.EN_track_check.EN_track_headers = {}

    def tearDown(self):
        del qctests.EN_track_check.EN_track_results
        del qctests.EN_track_check.EN_track_headers

    def trackSpeed_test(self):
        '''
        spot check on trackSpeed function
        '''

        # some fake profiles
        profiles = []
        # first 5 profiles in a straight line
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=2, longitude=90, date=[1999, 12, 31, 2]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=3, longitude=90, date=[1999, 12, 31, 3]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=4, longitude=90, date=[1999, 12, 31, 4]))
        # reverse one
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=3, longitude=90, date=[1999, 12, 31, 5]))

        trueDistance = util.geo.haversineDistance(profiles[0], profiles[1])
        trueSpeed = (trueDistance - self.distRes)/max(3600., self.timeRes)

        assert qctests.EN_track_check.trackSpeed(profiles[0], profiles[1]) == trueSpeed

    def detectExcessiveSpeed_test(self):
        '''
        spot checks on excessive speed flag
        '''

        speeds = [-1, 10,9,9,9,20]
        angles = [-1, 0, math.pi, 0, 0, None]

        assert qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 1, 2), 'failed to flag a speed in excess of max speed'
        assert qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 2, 10), 'failed to flag moderate speed at high angle'
        assert not qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 4, 10), 'flagged a moderate speed at small angle'


    def calculateTraj_test(self):
        '''
        spot check on trajectory summary
        '''

        # some fake profiles
        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=2, longitude=90, date=[1999, 12, 31, 2]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=3, longitude=90, date=[1999, 12, 31, 3]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=4, longitude=90, date=[1999, 12, 31, 4]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=3, longitude=90, date=[1999, 12, 31, 5]))

        trueSpeeds = [None]
        trueAngles = [None, 0, 0, 0, math.pi, None]

        for i in range(len(profiles)-1):
            trueDistance = util.geo.haversineDistance(profiles[i], profiles[i+1])
            trueSpeed = (trueDistance - self.distRes)/max(3600., self.timeRes)
            trueSpeeds.append(trueSpeed)

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        assert numpy.array_equal(speeds, trueSpeeds)
        assert numpy.array_equal(angles, trueAngles)

    def meanSpeed_test(self):
        '''
        make sure mean speed rejects speeds that are too fast
        '''

        profiles = []

        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 3]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=39, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=40, longitude=90, date=[1999, 12, 31, 9]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        individualSpeed = qctests.EN_track_check.trackSpeed(profiles[0], profiles[1])

        ms = qctests.EN_track_check.meanSpeed(speeds, profiles, 15)

        assert ms - individualSpeed < 1E-10, 'all steps between profiles were equal except for one that should have been dropped => mean speed should equal speed between two adjacent profiles'

    def condition_a_fast_test(self):
        '''
        condition a checks that the speed from 2->3 isn't too fast
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.01, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 2]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)[0]

        assert flag == 1, 'should have rejected the second profile due to high speed from second to third profile.'

    def condition_a_angle_test(self):
        '''
        condition a checks that the angle at 3 isn't too large
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.5, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 2]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.5, longitude=90, date=[1999, 12, 31, 3]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)[0]

        assert flag == 1, 'should have rejected the second profile due to high angle at third profile.'

    def condition_a_speed2_test(self):
        '''
        condition a rejects the first profile if the speed from 1->3 is too large
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.5, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=2, longitude=90, date=[1999, 12, 31, 2]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)[0]

        assert flag == 0, 'should have rejected the first profile due to high speed from first to third.'

    def condition_a_nominal_test(self):
        '''
        condition a rejects the first profile if the second passes muster
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.5, longitude=90, date=[1999, 12, 31, 1]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 2]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)[0]

        assert flag == 0, 'should have rejected the first profile since the second seems ok.'

    def condition_a_fast_end_test(self):
        '''
        speed test at end of profile
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.49, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10]))
        
        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)[0]
        
        assert flag == 4, 'should have rejected the second to last profile due to high speed from third to last to second to last profile.'

    def condition_a_angle_end_test(self):
        '''
        angle test at end of profile
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)[0]

        assert flag == 4, 'should have rejected the second to last profile due to high angle at third to final profile.'

    def condition_a_nominal_end_test(self):
        '''
        condition a rejects the last profile if the second to last passes muster
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)[0]

        assert flag == 5, 'should have rejected the last profile since the second to last seems ok.'

    def condition_b_test(self):
        '''
        nominal behavior of condition b
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_b(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'speed 4 too fast, speed 3 too fast -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_b(profiles, speeds, angles, 4, 15)[0]

        assert flag == 4, 'speed 4 too fast, speed 5 too fast -> should reject 4'

    def condition_c_test(self):
        '''
        nominal behavior of condition c
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_c(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'speed 4 too fast, speed 3 to 5 too fast -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15.5, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_c(profiles, speeds, angles, 4, 15)[0]

        assert flag == 4, 'speed 4 too fast, speed 2 to 4 too fast -> should reject 4'

    def condition_d_test(self):
        '''
        nominal behavior of condition d
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_d(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'speed 4 too fast, angle at 3 too large -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_d(profiles, speeds, angles, 4, 15)[0]
        
        assert flag == 4, 'speed 4 too fast, angle at 4 too large -> should reject 4'

    def condition_e_test(self):
        '''
        nominal behavior of condition e
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15.5, longitude=90, date=[1999, 12, 31, 10]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15, longitude=90, date=[1999, 12, 31, 11]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_e(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'speed 4 too fast, angle at 2 too large -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 11]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_e(profiles, speeds, angles, 4, 15)[0]
        
        assert flag == 4, 'speed 4 too fast, angle at 5 too large -> should reject 4'

    def condition_f_test(self):
        '''
        nominal behavior of condition f
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_f(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'speed 4 too fast, speed 3 very small -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_f(profiles, speeds, angles, 4, 15)[0]
        
        assert flag == 4, 'speed 4 too fast, speed 5 very small -> should reject 4'

    def condition_g_test(self):
        '''
        nominal behavior of condition g
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=10, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_g(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'positions 2, 4 and 5 all closely clustered but 3 far away -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=10, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_g(profiles, speeds, angles, 4, 15)[0]
        
        assert flag == 4, 'positions 2, 3 and 5 closely clustered but 4 far away -> should reject 4'

    def condition_h_test(self):
        '''
        nominal behavior of condition h
        '''

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_h(profiles, speeds, angles, 4, 15)[0]

        assert flag == 3, 'nonsmooth behavior at profile 3 -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_h(profiles, speeds, angles, 4, 15)[0]
        
        assert flag == 4, 'nonsmooth behavior at 4 -> should reject 4'

    ############################
    # Integration Tests 
    ############################

    def all_for_one_test(self):
        '''
        10 profiles in a straight slow line should pass
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 11], cruise=1000, uid=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=8))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[1999, 12, 31, 13], cruise=1000, uid=9))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.5, longitude=90, date=[1999, 12, 31, 14], cruise=1000, uid=10))

        # pass in any arbitrary profiles should catch all of them
        qctests.EN_track_check.test(ds.threadProfiles[3])
        truth = {}

        for i in range(1,11):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'all profiles on a nominal profile should pass no matter which one is provided to EN_track'

    def multi_track_test(self):
        '''
        a wild outlier on a different track shouldn't hurt anything
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.5, longitude=10, date=[1999, 12, 31, 9.5], cruise=1001, uid=11))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 11], cruise=1000, uid=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=8))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[1999, 12, 31, 13], cruise=1000, uid=9))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.5, longitude=90, date=[1999, 12, 31, 14], cruise=1000, uid=10))

        qctests.EN_track_check.test(ds.threadProfiles[3])
        truth = {}

        for i in range(1,11):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'profiles from a different track should not cause failures'

    def wild_outlier_test(self):
        '''
        flag an extreme outlier
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=10, date=[1999, 12, 31, 9.5], cruise=1000, uid=11))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 11], cruise=1000, uid=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=8))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[1999, 12, 31, 13], cruise=1000, uid=9))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.5, longitude=90, date=[1999, 12, 31, 14], cruise=1000, uid=10))

        qctests.EN_track_check.test(ds.threadProfiles[3])

        assert numpy.array_equal(numpy.ones(1, dtype=bool), qctests.EN_track_check.EN_track_results[(1000,11)]), 'should reject wild outlier'

    def condition_i_gap_test(self):
        '''
        if removing a profile makes an excessive speed between m-1 and m+1, remove both m and m-1.
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 30, 7], cruise=1000, uid=3))

        #end of first pass: reject on (i)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))

        #first pass: reject on (b)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[1999, 12, 31, 11], cruise=1000, uid=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.5, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=8))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21, longitude=90, date=[1999, 12, 31, 13], cruise=1000, uid=9))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.5, longitude=90, date=[1999, 12, 31, 14], cruise=1000, uid=10))

        qctests.EN_track_check.test(ds.threadProfiles[7])

        truth = {}
        for i in range(1,11):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)
        truth[(1000, 5)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (b) & (i) reject'


    def condition_c_integration_test(self):
        '''
        track passes until condition c
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        #first pass: reject profile[2] on (c)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        #inital speed check: flag profile[3]
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))

        qctests.EN_track_check.test(ds.threadProfiles[3])

        truth = {}
        for i in range(1,7):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 3)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (c) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 3, 15)[1]
        assert flag == 'c', 'Correct profile flagged, but not by the expected step.'

    def condition_d_integration_test(self):
        '''
        track passes until condition d
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        #initial speed check: flag profile[3]
        #first pass: reject profile[3] on (d)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))

        qctests.EN_track_check.test(ds.threadProfiles[5])

        truth = {}
        for i in range(1,7):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (d) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 3, 15)[1]
        assert flag == 'd', 'Correct profile flagged, but not by the expected step.'

    def condition_e_integration_test(self):
        '''
        track passes until condition e
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 30, 7], cruise=1000, uid=3))
        #first pass: reject profile[3] on (e)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        #initial speed check: flag profile[4]
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15, longitude=90, date=[2000, 01, 01, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=14.5, longitude=90, date=[2000, 01, 01, 11], cruise=1000, uid=7))

        qctests.EN_track_check.test(ds.threadProfiles[5])

        truth = {}
        for i in range(1,8):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (e) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 4, 15)[1]
        assert flag == 'e', 'Correct profile flagged, but not by the expected step.'

    def condition_f_integration_test(self):
        '''
        track passes until condition f
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 1], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 3], cruise=1000, uid=2))
        #first pass: reject profile[2] on (f)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=3))
        #initial speed check: flag profile[3]
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 11], cruise=1000, uid=5))

        qctests.EN_track_check.test(ds.threadProfiles[4])

        truth = {}
        for i in range(1,6):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 3)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (f) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 3, 15)[1]
        print flag
        assert flag == 'f', 'Correct profile flagged, but not by the expected step.'

    def condition_g_integration_test(self):
        '''
        track passes until condition g
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1998, 12, 31, 1], cruise=1000, uid=1))
        #first pass: reject profile[1] on (g)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=89, date=[1999, 12, 31, 1], cruise=1000, uid=2))
        #inital speed check: flag profile[2]
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 2], cruise=1000, uid=3))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[2000, 12, 31, 3], cruise=1000, uid=4))

        qctests.EN_track_check.test(ds.threadProfiles[3])

        truth = {}
        for i in range(1,5):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 2)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (g) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 2, 15)[1]
        assert flag == 'g', 'Correct profile flagged, but not by the expected step.'

    def condition_h_integration_test(self):
        '''
        track passes until condition h
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 15], cruise=1000, uid=3))
        #initial speed check: flag profile [3]
        #first pass: reject profile[3] on (h)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 16], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20, longitude=90, date=[1999, 12, 31, 20], cruise=1000, uid=5))
        #PD1: 1/3
        #PD2: 2/3
        #PT1: 3/8
        #PT2: 1/2

        qctests.EN_track_check.test(ds.threadProfiles[4])

        truth = {}
        for i in range(1,6):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (h) reject'

        speeds, angles = qctests.EN_track_check.calculateTraj(ds.threadProfiles)
        flag = qctests.EN_track_check.condition_a(ds.threadProfiles, speeds, angles, 3, 15)[1]
        assert flag == 'h', 'Correct profile flagged, but not by the expected step.'

    def unusual_case_one_prof_test(self):
        '''
        spot check on handling of cruise with only one profile.
        '''

        # Some fake profiles
        ds.threadProfiles = []

        # Only one profile available.
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0], cruise=1000, uid=1))

        assert qctests.EN_track_check.test(ds.threadProfiles[0]) == False, 'Failed to handle single profile'

    def unusual_case_no_time_test(self):
        '''
        spot check on handling of profiles with incomplete data (missing time)
        '''

        # Some fake profiles
        ds.threadProfiles = []

        # Time is missing.
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 1], cruise=1000, uid=2))
        ds.threadProfiles[0].primary_header['Time'] = None

        assert qctests.EN_track_check.test(ds.threadProfiles[0]) == False, 'Failed to handle missing time'

    def unusual_case_identical_positions_test(self):
        '''
        spot check on handling of profiles with incomplete data (identical positions)
        '''

        # Some fake profiles
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 1], cruise=1000, uid=2))

        assert qctests.EN_track_check.test(ds.threadProfiles[0]) == False, 'Failed to handle identical positions'

    def unusual_case_identical_times_test(self):
        '''
        spot check on handling of profiles with incomplete data (identical times)
        '''

        # Some fake profiles
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 0], cruise=1000, uid=2))

        assert qctests.EN_track_check.test(ds.threadProfiles[0]) == True, 'Failed to handle identical times'

    def real_case_1_test(self):
        '''
        A real instance of a series of a track with a failed track check reject.
        '''
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.230000, longitude=-22.220000, date=[1925, 6, 3, 12.000000], cruise=45, uid=72, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=80.050000, longitude=12.000000, date=[1925, 6, 5, 12.000000], cruise=45, uid=112, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=80.470000, longitude=11.080000, date=[1925, 6, 6, 12.000000], cruise=45, uid=130, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=80.470000, longitude=12.000000, date=[1925, 6, 6, 12.000000], cruise=45, uid=134, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=80.130000, longitude=12.000000, date=[1925, 6, 6, 12.000000], cruise=45, uid=137, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.930000, longitude=-52.680000, date=[1925, 6, 9, 12.000000], cruise=45, uid=189, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.430000, longitude=-50.230000, date=[1925, 6, 15, 12.000000], cruise=45, uid=301, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.430000, longitude=-50.220000, date=[1925, 6, 15, 12.000000], cruise=45, uid=303, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.430000, longitude=-50.650000, date=[1925, 6, 16, 12.000000], cruise=45, uid=316, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=68.830000, longitude=-52.800000, date=[1925, 6, 22, 12.000000], cruise=45, uid=489, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.030000, longitude=-52.620000, date=[1925, 6, 28, 12.000000], cruise=45, uid=577, probe_type=7))
        qc= [False, False, False, False, True, False, False, False, False, False, False]

        tcqc = []
        for p in ds.threadProfiles:
            tcqc.append(qctests.EN_track_check.test(p)[0])

        assert numpy.array_equal(qc, tcqc), 'QC results do not match those produced by EN system'

    def real_case_2_test(self):
        '''
        A real instance of a series of a track with a failed track check reject.
        '''
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.350000, longitude=-13.520000, date=[1925, 6, 11, 15.170000], cruise=843883, uid=222, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.300000, longitude=-13.000000, date=[1925, 6, 12, 11.830000], cruise=843883, uid=252, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.500000, longitude=-12.420000, date=[1925, 6, 12, 17.830000], cruise=843883, uid=256, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.820000, longitude=-12.430000, date=[1925, 6, 12, 23.330000], cruise=843883, uid=260, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.820000, longitude=-12.430000, date=[1925, 6, 12, 12.000000], cruise=843883, uid=261, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.500000, longitude=-12.420000, date=[1925, 6, 12, 12.000000], cruise=843883, uid=262, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.750000, longitude=-14.170000, date=[1925, 6, 13, 14.500000], cruise=843883, uid=272, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.270000, longitude=-14.370000, date=[1925, 6, 14, 2.750000], cruise=843883, uid=277, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.570000, longitude=-15.420000, date=[1925, 6, 14, 14.670000], cruise=843883, uid=279, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.600000, longitude=-16.450000, date=[1925, 6, 14, 18.500000], cruise=843883, uid=280, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.320000, longitude=-16.670000, date=[1925, 6, 15, 11.500000], cruise=843883, uid=289, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.020000, longitude=-17.400000, date=[1925, 6, 15, 18.500000], cruise=843883, uid=297, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.220000, longitude=-18.080000, date=[1925, 6, 17, 8.830000], cruise=843883, uid=325, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.350000, longitude=-18.320000, date=[1925, 6, 17, 12.500000], cruise=843883, uid=327, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.280000, longitude=-19.220000, date=[1925, 6, 17, 20.000000], cruise=843883, uid=331, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.180000, longitude=-20.170000, date=[1925, 6, 18, 0.500000], cruise=843883, uid=350, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.720000, longitude=-20.370000, date=[1925, 6, 18, 7.500000], cruise=843883, uid=351, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.080000, longitude=-20.930000, date=[1925, 6, 18, 13.500000], cruise=843883, uid=356, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.350000, longitude=-21.370000, date=[1925, 6, 18, 17.500000], cruise=843883, uid=358, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.530000, longitude=-22.050000, date=[1925, 6, 18, 23.000000], cruise=843883, uid=359, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.630000, longitude=-23.130000, date=[1925, 6, 19, 21.000000], cruise=843883, uid=378, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.600000, longitude=-23.380000, date=[1925, 6, 20, 1.750000], cruise=843883, uid=389, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=66.380000, longitude=-23.770000, date=[1925, 6, 20, 6.250000], cruise=843883, uid=392, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.830000, longitude=-23.950000, date=[1925, 6, 20, 14.500000], cruise=843883, uid=394, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.770000, longitude=-25.500000, date=[1925, 6, 20, 22.000000], cruise=843883, uid=396, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=65.270000, longitude=-24.780000, date=[1925, 6, 21, 5.420000], cruise=843883, uid=414, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.880000, longitude=-24.220000, date=[1925, 6, 21, 10.500000], cruise=843883, uid=418, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.550000, longitude=-23.430000, date=[1925, 6, 21, 19.000000], cruise=843883, uid=429, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.180000, longitude=-23.280000, date=[1925, 6, 22, 0.000000], cruise=843883, uid=462, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.230000, longitude=-22.220000, date=[1925, 6, 22, 6.000000], cruise=843883, uid=467, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.230000, longitude=-22.220000, date=[1925, 6, 24, 5.670000], cruise=843883, uid=503, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.130000, longitude=-22.400000, date=[1925, 6, 24, 11.000000], cruise=843883, uid=510, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=64.100000, longitude=-22.570000, date=[1925, 6, 24, 15.000000], cruise=843883, uid=512, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.870000, longitude=-22.820000, date=[1925, 6, 26, 1.500000], cruise=843883, uid=526, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.800000, longitude=-23.080000, date=[1925, 6, 26, 7.000000], cruise=843883, uid=528, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.670000, longitude=-22.800000, date=[1925, 6, 26, 23.000000], cruise=843883, uid=535, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.730000, longitude=-21.580000, date=[1925, 6, 27, 8.170000], cruise=843883, uid=547, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.320000, longitude=-20.800000, date=[1925, 6, 27, 16.000000], cruise=843883, uid=549, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.570000, longitude=-20.430000, date=[1925, 6, 27, 22.000000], cruise=843883, uid=550, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.300000, longitude=-20.080000, date=[1925, 6, 30, 13.000000], cruise=843883, uid=598, probe_type=7))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=63.420000, longitude=-19.420000, date=[1925, 6, 30, 21.000000], cruise=843883, uid=602, probe_type=7))
        qc= [False, True, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

        tcqc = []
        for p in ds.threadProfiles:
            tcqc.append(qctests.EN_track_check.test(p)[0])

        assert numpy.array_equal(qc, tcqc), 'QC results do not match those produced by EN system'

    def real_case_3_test(self):
        '''
        A real instance of a series of a track with a failed track check reject.
        '''
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=46.230000, longitude=-7.430000, date=[1975, 6, 3, 17.000000], cruise=9710419, uid=841, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.820000, longitude=-17.330000, date=[1975, 6, 10, 16.250000], cruise=9710419, uid=1419, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.680000, longitude=-17.400000, date=[1975, 6, 10, 19.420000], cruise=9710419, uid=1433, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.220000, longitude=-17.430000, date=[1975, 6, 11, 9.250000], cruise=9710419, uid=1486, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.530000, longitude=-17.430000, date=[1975, 6, 12, 3.080000], cruise=9710419, uid=1543, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.330000, longitude=-17.450000, date=[1975, 6, 12, 4.420000], cruise=9710419, uid=1547, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.170000, longitude=-17.500000, date=[1975, 6, 12, 5.580000], cruise=9710419, uid=1548, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=21.000000, longitude=-17.580000, date=[1975, 6, 12, 7.080000], cruise=9710419, uid=1556, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.830000, longitude=-17.630000, date=[1975, 6, 12, 10.080000], cruise=9710419, uid=1566, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.670000, longitude=-17.630000, date=[1975, 6, 12, 11.330000], cruise=9710419, uid=1569, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.670000, date=[1975, 6, 12, 14.920000], cruise=9710419, uid=1584, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.330000, longitude=-17.650000, date=[1975, 6, 12, 19.250000], cruise=9710419, uid=1607, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.170000, longitude=-17.650000, date=[1975, 6, 12, 21.000000], cruise=9710419, uid=1610, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.000000, longitude=-17.570000, date=[1975, 6, 12, 22.250000], cruise=9710419, uid=1614, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.170000, longitude=-17.580000, date=[1975, 6, 14, 8.670000], cruise=9710419, uid=1739, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.200000, longitude=-17.620000, date=[1975, 6, 14, 18.000000], cruise=9710419, uid=1779, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.350000, longitude=-17.620000, date=[1975, 6, 15, 2.500000], cruise=9710419, uid=1804, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.100000, longitude=-17.600000, date=[1975, 6, 15, 14.920000], cruise=9710419, uid=1841, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.250000, longitude=-17.630000, date=[1975, 6, 15, 18.580000], cruise=9710419, uid=1851, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.250000, longitude=-17.600000, date=[1975, 6, 16, 5.000000], cruise=9710419, uid=1880, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.130000, longitude=-17.570000, date=[1975, 6, 16, 9.000000], cruise=9710419, uid=1899, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.380000, longitude=-17.630000, date=[1975, 6, 16, 19.330000], cruise=9710419, uid=1943, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.630000, longitude=-17.650000, date=[1975, 6, 17, 0.000000], cruise=9710419, uid=1961, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.250000, longitude=-17.600000, date=[1975, 6, 17, 19.330000], cruise=9710419, uid=2041, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.120000, longitude=-17.620000, date=[1975, 6, 18, 0.500000], cruise=9710419, uid=2059, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.180000, longitude=-17.500000, date=[1975, 6, 18, 21.580000], cruise=9710419, uid=2137, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.000000, longitude=-17.670000, date=[1975, 6, 19, 0.500000], cruise=9710419, uid=2159, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.170000, longitude=-17.700000, date=[1975, 6, 19, 2.500000], cruise=9710419, uid=2162, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.350000, longitude=-17.700000, date=[1975, 6, 19, 4.830000], cruise=9710419, uid=2171, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.700000, date=[1975, 6, 19, 6.500000], cruise=9710419, uid=2179, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.600000, date=[1975, 6, 19, 20.670000], cruise=9710419, uid=2273, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.620000, longitude=-17.650000, date=[1975, 6, 19, 22.250000], cruise=9710419, uid=2282, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.920000, longitude=-17.500000, date=[1975, 6, 20, 21.580000], cruise=9710419, uid=2365, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.000000, longitude=-17.670000, date=[1975, 6, 21, 0.166944], cruise=9710419, uid=2376, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.170000, longitude=-17.700000, date=[1975, 6, 21, 2.420000], cruise=9710419, uid=2385, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.330000, longitude=-17.700000, date=[1975, 6, 21, 4.000000], cruise=9710419, uid=2392, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.700000, date=[1975, 6, 21, 6.170000], cruise=9710419, uid=2402, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.630000, longitude=-17.650000, date=[1975, 6, 21, 7.670000], cruise=9710419, uid=2409, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.580000, date=[1975, 6, 23, 9.330000], cruise=9710419, uid=2633, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.670000, longitude=-17.630000, date=[1975, 6, 23, 18.170000], cruise=9710419, uid=2698, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.900000, longitude=-17.480000, date=[1975, 6, 23, 20.170000], cruise=9710419, uid=2709, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.970000, longitude=-17.430000, date=[1975, 6, 24, 20.420000], cruise=9710419, uid=2806, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.800000, longitude=-17.430000, date=[1975, 6, 25, 0.500000], cruise=9710419, uid=2824, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.830000, longitude=-17.500000, date=[1975, 6, 26, 6.170000], cruise=9710419, uid=2928, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.920000, longitude=-17.500000, date=[1975, 6, 26, 10.170000], cruise=9710419, uid=2940, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.950000, longitude=-17.480000, date=[1975, 6, 27, 6.920000], cruise=9710419, uid=3016, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.670000, longitude=-17.630000, date=[1975, 6, 27, 14.670000], cruise=9710419, uid=3053, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.500000, longitude=-17.680000, date=[1975, 6, 27, 15.750000], cruise=9710419, uid=3061, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.330000, longitude=-17.650000, date=[1975, 6, 27, 16.920000], cruise=9710419, uid=3063, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.670000, longitude=-17.630000, date=[1975, 6, 27, 18.170000], cruise=9710419, uid=3070, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.000000, longitude=-17.570000, date=[1975, 6, 27, 19.170000], cruise=9710419, uid=3077, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.830000, longitude=-17.500000, date=[1975, 6, 27, 20.170000], cruise=9710419, uid=3080, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.670000, longitude=-17.450000, date=[1975, 6, 27, 21.330000], cruise=9710419, uid=3085, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.500000, longitude=-17.400000, date=[1975, 6, 27, 22.420000], cruise=9710419, uid=3088, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.330000, longitude=-17.670000, date=[1975, 6, 28, 11.750000], cruise=9710419, uid=3112, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.000000, longitude=-17.580000, date=[1975, 6, 28, 13.330000], cruise=9710419, uid=3117, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.830000, longitude=-17.500000, date=[1975, 6, 28, 14.830000], cruise=9710419, uid=3121, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.670000, longitude=-17.450000, date=[1975, 6, 28, 15.920000], cruise=9710419, uid=3123, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.500000, longitude=-17.570000, date=[1975, 6, 28, 17.000000], cruise=9710419, uid=3128, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.330000, longitude=-17.330000, date=[1975, 6, 28, 18.000000], cruise=9710419, uid=3129, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.170000, longitude=-17.300000, date=[1975, 6, 28, 19.000000], cruise=9710419, uid=3133, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.000000, longitude=-17.180000, date=[1975, 6, 28, 20.170000], cruise=9710419, uid=3135, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.830000, longitude=-17.080000, date=[1975, 6, 28, 21.250000], cruise=9710419, uid=3140, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.600000, longitude=-17.630000, date=[1975, 6, 30, 6.330000], cruise=9710419, uid=3205, probe_type=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=20.650000, longitude=-17.650000, date=[1975, 6, 30, 19.500000], cruise=9710419, uid=3244, probe_type=1))
        qc= [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

        tcqc = []
        for p in ds.threadProfiles:
            tcqc.append(qctests.EN_track_check.test(p)[0])

        assert numpy.array_equal(qc, tcqc), 'QC results do not match those produced by EN system'

    def real_case_4_test(self):
        '''
        A real instance of a series of a track with a failed track check reject.
        '''
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=59.070000, longitude=-18.920000, date=[1975, 6, 1, 7.580000], cruise=5546547, uid=8104, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=59.270000, longitude=-18.730000, date=[1975, 6, 4, 18.430000], cruise=5546547, uid=8593, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=56.450000, longitude=-10.330000, date=[1975, 6, 7, 15.250000], cruise=5546547, uid=9026, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=57.280000, longitude=-13.120000, date=[1975, 6, 8, 2.830000], cruise=5546547, uid=9097, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.300000, longitude=-17.000000, date=[1975, 6, 8, 8.170000], cruise=5546547, uid=9137, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=57.750000, longitude=-14.770000, date=[1975, 6, 8, 10.050000], cruise=5546547, uid=9148, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.000000, longitude=-15.880000, date=[1975, 6, 8, 15.030000], cruise=5546547, uid=9182, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=57.580000, longitude=-14.670000, date=[1975, 6, 8, 21.080000], cruise=5546547, uid=9235, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=57.220000, longitude=-13.630000, date=[1975, 6, 9, 2.080000], cruise=5546547, uid=9278, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=56.450000, longitude=-10.780000, date=[1975, 6, 9, 15.020000], cruise=5546547, uid=9368, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=56.130000, longitude=-9.980000, date=[1975, 6, 9, 21.170000], cruise=5546547, uid=9410, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=59.020000, longitude=-19.200000, date=[1975, 6, 13, 9.580000], cruise=5546547, uid=9989, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=59.220000, longitude=-19.400000, date=[1975, 6, 16, 21.400000], cruise=5546547, uid=10516, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.770000, longitude=-19.420000, date=[1975, 6, 22, 8.150000], cruise=5546547, uid=11446, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.730000, longitude=-19.330000, date=[1975, 6, 23, 1.000000], cruise=5546547, uid=11580, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.850000, longitude=-19.400000, date=[1975, 6, 23, 10.250000], cruise=5546547, uid=11644, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.820000, longitude=-19.420000, date=[1975, 6, 24, 7.720000], cruise=5546547, uid=11821, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.820000, longitude=-19.380000, date=[1975, 6, 25, 9.670000], cruise=5546547, uid=12029, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.750000, longitude=-19.400000, date=[1975, 6, 26, 8.250000], cruise=5546547, uid=12208, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.830000, longitude=-19.620000, date=[1975, 6, 27, 9.000000], cruise=5546547, uid=12370, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.770000, longitude=-19.550000, date=[1975, 6, 28, 8.000000], cruise=5546547, uid=12515, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=58.750000, longitude=-19.580000, date=[1975, 6, 29, 7.920000], cruise=5546547, uid=12647, probe_type=2))
        qc= [False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

        tcqc = []
        for p in ds.threadProfiles:
            tcqc.append(qctests.EN_track_check.test(p)[0])

        assert numpy.array_equal(qc, tcqc), 'QC results do not match those produced by EN system'

    def real_case_5_test(self):
        '''
        A real instance of a series of a track with a failed track check reject.
        '''
        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-20.920000, longitude=112.862000, date=[1975, 6, 7, 18.000000], cruise=5670710, uid=9040, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-19.350000, longitude=113.795000, date=[1975, 6, 8, 0.020000], cruise=5670710, uid=9077, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-17.380000, longitude=114.162000, date=[1975, 6, 8, 6.000000], cruise=5670710, uid=9116, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-15.500000, longitude=115.512000, date=[1975, 6, 8, 12.000000], cruise=5670710, uid=9164, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-12.470000, longitude=114.800000, date=[1975, 6, 8, 18.000000], cruise=5670710, uid=9212, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-10.980000, longitude=115.220000, date=[1975, 6, 9, 0.020000], cruise=5670710, uid=9257, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-9.370000, longitude=115.580000, date=[1975, 6, 9, 7.000000], cruise=5670710, uid=9323, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-7.750000, longitude=115.050000, date=[1975, 6, 9, 12.000000], cruise=5670710, uid=9360, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-6.630000, longitude=116.700000, date=[1975, 6, 9, 18.000000], cruise=5670710, uid=9384, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-3.700000, longitude=118.130000, date=[1975, 6, 10, 0.020000], cruise=5670710, uid=9451, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=-1.770000, longitude=118.780000, date=[1975, 6, 10, 6.000000], cruise=5670710, uid=9481, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=0.267000, longitude=119.220000, date=[1975, 6, 10, 12.000000], cruise=5670710, uid=9527, probe_type=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=2.170000, longitude=119.480000, date=[1975, 6, 10, 18.000000], cruise=5670710, uid=9562, probe_type=2))
        qc= [False, False, False, True, True, False, False, False, True, False, False, False, False]

        tcqc = []
        for p in ds.threadProfiles:
            tcqc.append(qctests.EN_track_check.test(p)[0])

        assert numpy.array_equal(qc, tcqc), 'QC results do not match those produced by EN system'

