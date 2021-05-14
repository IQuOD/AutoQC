import qctests.EN_background_check
import qctests.EN_spike_and_step_check
import qctests.EN_increasing_depth_check
import qctests.EN_stability_check
import qctests.EN_constant_value_check
from util import main
import util.testingProfile
import numpy
from util.dbutils import retrieve_existing_qc_result

#####  ---------------------------------------------------

class TestClass:

    parameters = {
        'db': 'iquod.db',
        "table": 'unit'
    }
    qctests.EN_background_check.loadParameters(parameters)

    def setUp(self):
        # this qc test will go looking for the profile in question in the db, needs to find something sensible
        main.faketable('unit')
        main.fakerow('unit')
        # need to re-do this every time to refresh the enspikeandstep table
        qctests.EN_spike_and_step_check.loadParameters(self.parameters)

    def tearDown(self):
        main.dbinteract('DROP TABLE unit;')

    def test_retrieve_existing_qc_results_EN_background(self):
        '''
        Use one of the EN_background_check tests to check retrieve_existing_qc_results is working.
        '''
        
        test = 'en_background_check'
        
        # Create the test profile, run the QC check and save the result.
        # Expected result is [False, False, False, True].
        p = util.testingProfile.fakeProfile([1.8, 1.8, 1.8, 7.1], [0.0, 2.5, 5.0, 7.5], latitude=55.6, longitude=12.9, date=[1900, 1, 15, 0], probe_type=7, uid=8888) 
        qc = qctests.EN_background_check.test(p, self.parameters)
        query = "UPDATE " + self.parameters['table'] + " SET " + test + "=? WHERE uid=8888;"
        main.dbinteract(query, [main.pack_array(qc)], targetdb=self.parameters['db'])
        
        # Use the retrieve_existing_qc_result to read the result back from the database.
        retrieved_qc = retrieve_existing_qc_result(test, 8888, self.parameters['table'], self.parameters['db'])
        assert numpy.array_equal(qc, retrieved_qc), 'mismatch between qc results and retrieved values'

        # Also check against the expected result in case of database write/read mistake.
        expected = numpy.array([False, False, False, True])
        assert numpy.array_equal(expected, retrieved_qc), 'mismatch between expected and retrieved values'


    def test_retrieve_existing_qc_results_EN_increasing_depth(self):
        '''
        Use one of the EN_increasing_depth tests to check retrieve_existing_qc_results is working.
        '''
        
        test = 'en_increasing_depth_check'
        
        # Create the test profile, run the QC check and save the result.
        # Expected result is [False, False, False, True, True, False, False, False, False, False].
        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,500,500,600,700,800,900,1000], latitude=0.0, uid=8888)
        qc = qctests.EN_increasing_depth_check.test(p, self.parameters)
        query = "UPDATE " + self.parameters['table'] + " SET " + test + "=? WHERE uid=8888;"
        main.dbinteract(query, [main.pack_array(qc)], targetdb=self.parameters['db'])
        
        # Use the retrieve_existing_qc_result to read the result back from the database.
        retrieved_qc = retrieve_existing_qc_result(test, 8888, self.parameters['table'])     
        assert numpy.array_equal(qc, retrieved_qc), 'mismatch between qc results and retrieved values'
        
        # Also check against the expected result in case of database write/read mistake.
        expected = numpy.array([False, False, False, True, True, False, False, False, False, False])
        assert numpy.array_equal(expected, retrieved_qc), 'mismatch between expected and retrieved values'

        
    def test_retrieve_existing_qc_results_EN_stability_check(self):
        '''
        Use one of the EN_stability_check tests to check retrieve_existing_qc_results is working.
        '''
        
        test = 'en_stability_check'
        
        # Create the test profile, run the QC check and save the result.
        # Expected result is [False, True, True, False, False, False, False, False, False].
        p = util.testingProfile.fakeProfile([13.5, 25.5, 20.4, 13.5, 13.5, 13.5, 13.5, 13.5, 13.5], [0, 10, 20, 30, 40, 50, 60, 70, 80], salinities=[40, 35, 20, 40, 40, 40, 40, 40, 40], pressures=[8000, 2000, 1000, 8000, 8000, 8000, 8000, 8000, 8000], uid=8888)
        qc = qctests.EN_stability_check.test(p, self.parameters)
        query = "UPDATE " + self.parameters['table'] + " SET " + test + "=? WHERE uid=8888;"
        main.dbinteract(query, [main.pack_array(qc)], targetdb=self.parameters['db'])
        
        # Use the retrieve_existing_qc_result to read the result back from the database.
        retrieved_qc = retrieve_existing_qc_result(test, 8888, self.parameters['table'])       
        assert numpy.array_equal(qc, retrieved_qc), 'mismatch between qc results and retrieved values'

        # Also check against the expected result in case of database write/read mistake.
        expected = numpy.array([False, True, True, False, False, False, False, False, False])
        assert numpy.array_equal(expected, retrieved_qc), 'mismatch between expected and retrieved values'

    def test_retrieve_existing_qc_results_EN_constant_value(self):
        '''
        Use one of the EN_constant_value_check tests to check retrieve_existing_qc_results is working.
        '''
        
        test = 'en_constant_value_check'
        
        # Create the test profile, run the QC check and save the result.
        # Expected result is [True, True, True, True, True, True, True, True, True, True].
        p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,None], uid=8888)
        qc = qctests.EN_constant_value_check.test(p, self.parameters)
        query = "UPDATE " + self.parameters['table'] + " SET " + test + "=? WHERE uid=8888;"
        main.dbinteract(query, [main.pack_array(qc)], targetdb=self.parameters['db'])
        
        # Use the retrieve_existing_qc_result to read the result back from the database.
        retrieved_qc = retrieve_existing_qc_result(test, 8888, self.parameters['table']) 
        assert numpy.array_equal(qc, retrieved_qc), 'mismatch between qc results and retrieved values'

        # Also check against the expected result in case of database write/read mistake.
        expected = numpy.array([True, True, True, True, True, True, True, True, True, True])
        assert numpy.array_equal(expected, retrieved_qc), 'mismatch between expected and retrieved values'

    def test_retrieve_existing_qc_result_before_qc(self):
        '''
        Test that None is returned if a QC result has not been saved in the database.
        '''
        
        test = 'wod_range_check'
        retrieved_qc = retrieve_existing_qc_result(test, 8888, self.parameters['table'])
        
        assert retrieved_qc is 343, 'None not returned if QC not available'
        

        
