import util.main as main
import os, math
from wodpy import wod
import numpy, pandas
import util.testingProfile
import qctests.EN_track_check
import util.geo

class TestClass():
    # def setUp(self):

    distRes = 20000. #meters
    timeRes = 600.   #seconds

    #     # #create an incorrectly formatted list of input files
    #     # file = open("notalist.json", "w")
    #     # file.write('{"not": "alist"}')
    #     # file.close()

    #     # #create a list of input files that does not exist
    #     # file = open("dne.json", "w")
    #     # file.write('["data/doesnotexist.dat"]')
    #     # file.close()

    #     # #create an artificial profile to trigger the temperature flag
    #     # #sets first temperature to 99.9; otherwise identical to data/example.dat
    #     # file = open("temp.dat", "w")
    #     # file.write('C41303567064US5112031934 8 744210374426193562-17227140 6110101201013011182205814\n')
    #     # file.write('01118220291601118220291901024721 8STOCS85A3 41032151032165-500632175-50023218273\n')
    #     # file.write('18117709500110134401427143303931722076210220602291107291110329977020133023846181\n')
    #     # file.write('24421800132207614110217330103192220521322011216442103723077095001101818115508527\n')
    #     # file.write('20012110000133312500021011060022022068002272214830228442684000230770421200000191\n')
    #     # file.write('15507911800121100001333125000151105002103302270022022068002274411816302284426840\n')
    #     # file.write('00230770426500000191155069459001211000013331250001511050021033011300220220680022\n')
    #     # file.write('73319043022844268400023077042620000019116601596680012110000133312500021022016002\n')
    #     # file.write('17110100220220680022733112830228442684000230770435700000181155088803001211000013\n')
    #     # file.write('33125000210220160022022068002273311283022844268400023077042120000019115508880300\n')
    #     # file.write('12110000133312500015110200210330535002202206800227441428030228442684000230770421\n')
    #     # file.write('20000019115508880300121100001333125000152204300210220320022022068002273312563022\n')
    #     # file.write('84426840002307704212000001911550853710012110000133312500015110200210220160022022\n')
    #     # file.write('06800227331128302284426840002307704212000001100001319990044230900033267500222650\n')
    #     # file.write('03312050033281000220100033289500442309000332670002227100331123003328100022025002\n')
    #     # file.write('22900044231910033286200222900033115400332810002205000342-12300442324100332728003\n')
    #     # file.write('32117003312560033280500                                                         \n')
    #     # file.close()


    #     # return

    # def tearDown(self):

    #     return

    def trackSpeed_test(self):
        '''
        spot check on trackSpeed function
        '''

        first = util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=90, date=[1999, 12, 31, 0])
        last =  util.testingProfile.fakeProfile([0], [0], latitude=1, longitude=90, date=[1999, 12, 31, 1])

        trueDistance = util.geo.haversineDistance(first, last)
        trueSpeed = (trueDistance - self.distRes)/max(3600., self.timeRes)

        assert qctests.EN_track_check.trackSpeed(first, last) == trueSpeed

    def detectExcessiveSpeed_test(self):
        '''
        spot checks on excessive speed flag
        '''

        speeds = [10,9,9,20]
        angles = [math.pi, math.pi/4, math.pi/4]

        assert qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 0, 2), 'failed to flag a speed in excess of max speed'
        assert qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 1, 10), 'failed to flag moderate speed at high angle'
        assert not qctests.EN_track_check.detectExcessiveSpeed(speeds, angles, 2, 10), 'flagged a moderate speed at small angle'















