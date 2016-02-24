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

        trueSpeeds = [-1]
        trueAngles = [-1, 0, 0, 0, math.pi, None]

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 1, 15)

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)
        
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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)

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

        flag = qctests.EN_track_check.condition_a(profiles, speeds, angles, 5, 15)

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

        flag = qctests.EN_track_check.condition_b(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'speed 4 too fast, speed 3 too fast -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_b(profiles, speeds, angles, 4, 15)

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
        
        flag = qctests.EN_track_check.condition_c(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'speed 4 too fast, speed 3 to 5 too fast -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15.5, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)

        flag = qctests.EN_track_check.condition_c(profiles, speeds, angles, 4, 15)

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
        
        flag = qctests.EN_track_check.condition_d(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'speed 4 too fast, angle at 3 too large -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
    
        flag = qctests.EN_track_check.condition_d(profiles, speeds, angles, 4, 15)
        
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
    
        flag = qctests.EN_track_check.condition_e(profiles, speeds, angles, 4, 15)

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
        
        flag = qctests.EN_track_check.condition_e(profiles, speeds, angles, 4, 15)
        
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
    
        flag = qctests.EN_track_check.condition_f(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'speed 4 too fast, speed 3 very small -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_f(profiles, speeds, angles, 4, 15)
        
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
    
        flag = qctests.EN_track_check.condition_g(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'positions 2, 4 and 5 all closely clustered but 3 far away -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=10, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_g(profiles, speeds, angles, 4, 15)
        
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
    
        flag = qctests.EN_track_check.condition_h(profiles, speeds, angles, 4, 15)

        assert flag == 3, 'nonsmooth behavior at profile 3 -> should reject 3'

        profiles = []
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 5]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 6]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 8]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9]))
        profiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 10]))

        speeds, angles = qctests.EN_track_check.calculateTraj(profiles)
        
        flag = qctests.EN_track_check.condition_h(profiles, speeds, angles, 4, 15)
        
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

        #first pass: reject on (c)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
       
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=19, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))

        qctests.EN_track_check.test(ds.threadProfiles[3])

        truth = {}
        for i in range(1,7):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 3)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (c) reject'

    def condition_d_integration_test(self):
        '''
        track passes until condition d
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))

        #first pass: reject on (d)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))

        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 10], cruise=1000, uid=6))

        qctests.EN_track_check.test(ds.threadProfiles[5])

        truth = {}
        for i in range(1,7):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (d) reject'

    def condition_e_integration_test(self):
        '''
        track passes until condition e
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 30, 5], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 30, 6], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 30, 7], cruise=1000, uid=3))

        #first pass: reject on (e)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
       
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=15, longitude=90, date=[2000, 01, 01, 10], cruise=1000, uid=6))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=14.5, longitude=90, date=[2000, 01, 01, 11], cruise=1000, uid=7))

        qctests.EN_track_check.test(ds.threadProfiles[5])

        truth = {}
        for i in range(1,8):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 4)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (e) reject'

    def condition_f_integration_test(self):
        '''
        track passes until condition f
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 1], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16.5, longitude=90, date=[1999, 12, 31, 2], cruise=1000, uid=2))

        #first pass: reject on (f)
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 7], cruise=1000, uid=3))
        
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 8], cruise=1000, uid=4))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18.5, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=5))

        qctests.EN_track_check.test(ds.threadProfiles[4])

        truth = {}
        for i in range(1,6):
            truth[(1000, i)] = numpy.zeros(1, dtype=bool)
        truth[(1000, 3)] = numpy.ones(1, dtype=bool)

        assert numpy.array_equal(truth, qctests.EN_track_check.EN_track_results), 'condition (f) reject'

    def condition_h_integration_test(self):
        '''
        track passes until condition h
        '''

        ds.threadProfiles = []
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=16, longitude=90, date=[1999, 12, 31, 9], cruise=1000, uid=1))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=17, longitude=90, date=[1999, 12, 31, 12], cruise=1000, uid=2))
        ds.threadProfiles.append(util.testingProfile.fakeProfile([0], [0], latitude=18, longitude=90, date=[1999, 12, 31, 15], cruise=1000, uid=3))

        #first pass: reject on (h)
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




