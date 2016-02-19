import util.main as main
import os, math
from wodpy import wod
import numpy, pandas
import util.testingProfile
import qctests.EN_track_check
import util.geo

class TestClass():
    distRes = 20000. #meters
    timeRes = 600.   #seconds

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


    def trackSpeed_test(self):
        '''
        spot check on trackSpeed function
        '''

        trueDistance = util.geo.haversineDistance(self.profiles[0], self.profiles[1])
        trueSpeed = (trueDistance - self.distRes)/max(3600., self.timeRes)

        assert qctests.EN_track_check.trackSpeed(self.profiles[0], self.profiles[1]) == trueSpeed

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

        trueSpeeds = [-1]
        trueAngles = [-1, 0, 0, 0, math.pi, None]

        for i in range(len(self.profiles)-1):
            trueDistance = util.geo.haversineDistance(self.profiles[i], self.profiles[i+1])
            trueSpeed = (trueDistance - self.distRes)/max(3600., self.timeRes)
            trueSpeeds.append(trueSpeed)

        speeds, angles = qctests.EN_track_check.calculateTraj(self.profiles)

        assert numpy.array_equal(speeds, trueSpeeds)
        assert numpy.array_equal(angles, trueAngles)

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
        print speeds
        flag = qctests.EN_track_check.condition_c(profiles, speeds, angles, 4, 15)
        print flag
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
