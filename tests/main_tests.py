import util.main as main
import os
from wodpy import wod
import numpy, pandas
from pandas.util.testing import assert_frame_equal

class TestClass():
    def setUp(self):

        #create an incorrectly formatted list of input files
        file = open("notalist.json", "w")
        file.write('{"not": "alist"}')
        file.close()

        #create a list of input files that does not exist
        file = open("dne.json", "w")
        file.write('["data/doesnotexist.dat"]')
        file.close()

        #create an artificial profile to trigger the temperature flag
        #sets first temperature to 99.9; otherwise identical to data/example.dat
        file = open("temp.dat", "w")
        file.write('C41303567064US5112031934 8 744210374426193562-17227140 6110101201013011182205814\n')
        file.write('01118220291601118220291901024721 8STOCS85A3 41032151032165-500632175-50023218273\n')
        file.write('18117709500110134401427143303931722076210220602291107291110329977020133023846181\n')
        file.write('24421800132207614110217330103192220521322011216442103723077095001101818115508527\n')
        file.write('20012110000133312500021011060022022068002272214830228442684000230770421200000191\n')
        file.write('15507911800121100001333125000151105002103302270022022068002274411816302284426840\n')
        file.write('00230770426500000191155069459001211000013331250001511050021033011300220220680022\n')
        file.write('73319043022844268400023077042620000019116601596680012110000133312500021022016002\n')
        file.write('17110100220220680022733112830228442684000230770435700000181155088803001211000013\n')
        file.write('33125000210220160022022068002273311283022844268400023077042120000019115508880300\n')
        file.write('12110000133312500015110200210330535002202206800227441428030228442684000230770421\n')
        file.write('20000019115508880300121100001333125000152204300210220320022022068002273312563022\n')
        file.write('84426840002307704212000001911550853710012110000133312500015110200210220160022022\n')
        file.write('06800227331128302284426840002307704212000001100001319990044230900033267500222650\n')
        file.write('03312050033281000220100033289500442309000332670002227100331123003328100022025002\n')
        file.write('22900044231910033286200222900033115400332810002205000342-12300442324100332728003\n')
        file.write('32117003312560033280500                                                         \n')
        file.close()


        return

    def tearDown(self):
        os.remove('notalist.json')
        os.remove('dne.json')
        os.remove('temp.dat')
        return

    def readInput_list_test(self):
        '''
        main.readInput should assert it gets a list back
        '''

        try:
            main.readInput('notalist.json')
        except AssertionError:
            assert True
            return

        assert False, "readInput failed to raise an exception when given json that wasn't a list"

    def reatInput_dne_test(self):
        '''
        main.readInput should raise exceptions if listed files don't exist
        '''

        try:
            main.readInput('dne.json')
        except AssertionError:
            assert True
            return

        assert False, "readInput failed to raise an exception when a listed data file was not found."

    def extractProfiles_test(self):
        '''
        simple check to make sure only WodProfile objects are getting returned
        '''

        profiles = main.extractProfiles(["data/quota_subset.dat"])
        for i in profiles:
            assert isinstance(i, wod.WodProfile), i + ' is not a WodProfile'

    def extractProfiles_example_test(self):
        '''
        check the example from pp 137 of
        http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
        is extracted correctly.
        data is in `data/example.dat`
        '''

        profile = main.extractProfiles(['data/example.dat'])[0]

        assert profile.latitude() == 61.930, 'incorrect latitude extraction'
        assert profile.longitude() == -172.270, 'incorrect longitude extraction'
        assert profile.uid() == 67064, 'incorrect UID extraction'
        assert profile.n_levels() == 4, 'incorrect # levels extraction'
        assert profile.year() == 1934, 'incorrect year extraction'
        assert profile.month() == 8, 'incorrect month extraction'
        assert profile.day() == 7, 'incorrect day extraction'
        assert profile.time() == 10.37, 'incorrect time extraction'
        assert profile.probe_type() == 7, 'incorrect probe type extraction'

    def profileData_example_test(self):
        '''
        continue examining data extracted from pp 137 of
        http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
        '''

        profile = main.extractProfiles(['data/example.dat'])[0]
        current = ''
        p, current, f = main.profileData(profile, current, None)

        assert numpy.array_equal(p.z(), [0.0, 10.0, 25.0, 50.0])
        assert numpy.array_equal(p.z_level_qc(), [0,0,0,0])
        assert numpy.array_equal(p.t(), [8.960, 8.950, 0.900, -1.230])
        assert numpy.array_equal(p.t_level_qc(), [0,0,0,0])
        assert numpy.array_equal(p.s(), [30.900, 30.900, 31.910, 32.410])
        assert numpy.array_equal(p.s_level_qc(), [0,0,0,0])

    def importQC_test(self):
        '''
        make sure main.importQC returns a valid list of tests that actually exist
        '''

        tests = main.importQC("qctests")
        assert isinstance(tests, list), 'importQC did not return a list'

        for test in tests:
            assert os.path.isfile('qctests/'+test+'.py'), 'test ' + test + ' is not found.'

    def catchFlags_example_test(self):
        '''
        make sure main.catchFlags is flagging temperatures of 99.9 as missing,
        using the artificial data generated in temp.dat above.
        '''

        profile = main.extractProfiles(['temp.dat'])[0]
        current = ''
        p, current, f = main.profileData(profile, current, None)

        main.catchFlags(p)

        assert p.profile_data[0]['variables'][0]['Missing'], 'failed to flag a temperature of 99.9 as a missing value'

    def referenceResults_example_test(self):
        '''
        make sure main.referenceResults is extacting the correct references from data/example.dat
        '''

        profile = main.extractProfiles(['data/example.dat'])[0]
        current = ''
        p, current, f = main.profileData(profile, current, None)

        ref = main.referenceResults([p])

        assert ref[0][0] == False, 'incorrect extraction of overall reference result for data/example.dat'
        assert numpy.array_equal(ref[1][0], [False, False, False, False] ), 'incorrect extraction of verbose reference results for data/example.dat'

    def generateCSV_test(self):
        '''
        make sure things are being packed into dataframes correctly;
        assumes Pandas writes dataframes to csv correctly. 
        '''

        truth = [True, False, False]
        results = [
            [False, False, False],
            [True, True, True]
        ]
        tests = ['x', 'y']
        keys = [1000,1001,1002]

        df = main.generateCSV(truth, results, tests, keys, 'test')
        dfTrue = pandas.DataFrame([[True, False, True],[False, False, True],[False, False, True]], index=keys, columns=['True Flags', 'x', 'y'])

        assert_frame_equal(df, dfTrue, check_names=True)

    def parallelization_test(self):
        '''
        simple test to check parallelization infrastructure
        '''

        dummy.parallel = main.parallel_function(dummy)
        parallel_result = dummy.parallel([1,2])

        assert numpy.array_equal(parallel_result[0][0], [2,3])
        assert numpy.array_equal(parallel_result[0][1], [4,5])
        assert numpy.array_equal(parallel_result[1][0], [4,6])
        assert numpy.array_equal(parallel_result[1][1], [8,10])

    def combineArrays_test(self):
        '''
        spotcheck combineArrays
        '''

        parallel = [
            [[0,1],[[100,101],[102,103],[104,105]], [992,993]],
            [[2,3],[[200,201],[202,203],[204,205]], [994,995]],
            [[4,5],[[300,301],[302,303],[304,305]], [996,997]],
            [[6,7],[[400,401],[402,403],[404,405]], [998,999]]
        ]

        truth, results, ids = main.combineArrays(parallel)

        assert numpy.array_equal(truth, [0,1,2,3,4,5,6,7])
        assert numpy.array_equal(results, [ [100,101, 200,201, 300,301, 400,401], [102,103, 202,203, 302,303, 402,403], [104,105, 204,205, 304,305, 404,405] ])
        assert numpy.array_equal(ids, [992, 993, 994, 995, 996, 997, 998, 999])

def dummy(x):
    return [2*x, 3*x], [4*x, 5*x]




