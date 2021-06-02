import qctests.EN_background_check
import qctests.EN_spike_and_step_check
import qctests.EN_increasing_depth_check
import qctests.EN_stability_check
import qctests.EN_constant_value_check
from util import main
import util.testingProfile
import numpy
from util import dbutils
from util.dbutils import qc_action
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
        
        assert retrieved_qc is None, 'None not returned if QC not available'
        
    def test_get_n_levels_before_fail(self):
        '''
        Test that the correct number of levels before a reject is found.
        '''
        
        qc = [main.pack_array(numpy.array([False, False, True, False])),
              main.pack_array(numpy.array([False, False, False, False])),
              main.pack_array(numpy.array([True, True, True, True]))]
              
        n = dbutils.get_n_levels_before_fail(qc)
        
        expected = [2, 4, 0]
        
        assert numpy.array_equal(n, expected), 'Number of levels returned was not as expected'
         
    def test_get_reversed_n_levels_before_fail(self):
        '''
        Test that the correct number of levels before a reject is found, counting from the bottom.
        '''
        
        qc = [main.pack_array(numpy.array([False, False, True, False])),
              main.pack_array(numpy.array([False, False, False, False])),
              main.pack_array(numpy.array([True, True, True, True]))]
              
        n = dbutils.get_reversed_n_levels_before_fail(qc)
        
        expected = [-1, -4, 0]
        
        assert numpy.array_equal(n, expected), 'Number of levels returned was not as expected'
         
    def test_check_for_fail(self):
        '''
        Test that the correct number of levels before a reject is found, counting from the bottom.
        '''
        
        qc = [main.pack_array(numpy.array([False, False, True, False])),
              main.pack_array(numpy.array([False, False, False, False])),
              main.pack_array(numpy.array([True, True, True, True]))]
              
        results = dbutils.check_for_fail(qc)
        
        expected = [True, False, True]
        
        assert numpy.array_equal(results, expected), 'Result not as expected'
        
    def update_qc(self, uid, test, qc):
        # Useful function to update the database with some QC results.
        query = "UPDATE " + self.parameters['table'] + " SET " + test + "=? WHERE uid=" + str(uid) + ";"
        main.dbinteract(query, [main.pack_array(qc)], targetdb=self.parameters['db'])
        
    def test_dbtodf_parsed(self):
        '''
        Basic test of functionality to create the dataframe and parse results.
        '''
        
        # Define some QC results and check the parsing returns the expected result.
        self.update_qc(8888, 'truth', numpy.ma.array([1, 1, 1, 1]))
        self.update_qc(8888, 'en_track_check', numpy.ma.array([False, False, False, False]))
        self.update_qc(8888, 'en_range_check', numpy.ma.array([True, False, False, False]))
        df = dbutils.db_to_df('unit')
        assert df['Truth'][0] == False, 'QC results incorrect.'
        assert df['EN_track_check'][0] == False, 'QC results incorrect.'
        assert df['EN_range_check'][0] == True, 'QC results incorrect.'
        
        self.update_qc(8888, 'truth', numpy.ma.array([1, 1, 1, 4]))
        df = dbutils.db_to_df('unit')
        assert df['Truth'][0] == True, 'QC results incorrect.'
        
        self.update_qc(8888, 'truth', numpy.ma.array([1, 1, 1, 3]))
        df = dbutils.db_to_df('unit')
        assert df['Truth'][0] == True, 'QC results incorrect.'
        
        self.update_qc(8888, 'truth', numpy.ma.array([1, 1, 1, 3], mask=[False, False, False, True]))
        df = dbutils.db_to_df('unit')
        assert df['Truth'][0] == False, 'QC results incorrect.'

    def test_dbtodf_unparsed(self):
        '''
        Basic test of functionality to create the dataframe without parsing results.
        '''
        
        # Define some QC results and check the parsing returns the expected result.
        self.update_qc(8888, 'truth', numpy.ma.array([1, 2, 3, 4]))
        self.update_qc(8888, 'en_track_check', numpy.ma.array([False, False, True, False]))
        self.update_qc(8888, 'en_range_check', numpy.ma.array([True, False, False, False]))
        df = dbutils.db_to_df('unit', applyparse=False)
        assert numpy.array_equal(dbutils.unpack_qc(df['Truth'][0]), [1, 2, 3, 4]), 'QC results incorrect.'
        assert numpy.array_equal(dbutils.unpack_qc(df['EN_track_check'][0]), [False, False, True, False]), 'QC results incorrect.'
        assert numpy.array_equal(dbutils.unpack_qc(df['EN_range_check'][0]), [True, False, False, False]), 'QC results incorrect.'
        
    def test_qc_action_remove_above_reject(self):
        '''
        Check that qc_action correctly applies the actions.
        '''
        
        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([False, False, False, True, False, False])))
        expected = [True, True, True, True, False, False]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([True, False, False, False, False, False])))
        expected = [True, False, False, False, False, False]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([False, False, False, True, False, True])))
        expected = [True, True, True, True, True, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([False, False, False, False, False, False])))
        expected = [False, False, False, False, False, False]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([True, True, True, True, True, True])))
        expected = [True, True, True, True, True, True]
        assert numpy.array_equal(result, expected)

    def test_qc_action_remove_below_reject(self):
        '''
        Check that qc_action correctly applies the actions.
        '''
        
        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([False, False, False, True, False, False])))
        expected = [False, False, False, True, True, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([True, False, False, True, False, False])))
        expected = [True, True, True, True, True, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([False, False, False, False, False, True])))
        expected = [False, False, False, False, False, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([False, False, False, False, False, False])))
        expected = [False, False, False, False, False, False]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([True, True, True, True, True, True])))
        expected = [True, True, True, True, True, True]
        assert numpy.array_equal(result, expected)
                            
    def test_qc_action_remove_rejected_levels(self):
        '''
        Check that qc_action correctly applies the actions.
        '''
        
        result = qc_action('Remove rejected levels',
                           main.pack_array(numpy.array([True, False, False, True, False, False])))
        expected = [True, False, False, True, False, False]
        assert numpy.array_equal(result, expected)

    def test_qc_action_remove_profile(self):
        '''
        Check that qc_action correctly applies the actions.
        '''
        
        result = qc_action('Remove profile',
                           main.pack_array(numpy.array([True, False, False, True, False, False])))
        expected = [True, True, True, True, True, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove profile',
                           main.pack_array(numpy.array([False, False, False, False, False, False])))
        expected = [False, False, False, False, False, False]
        assert numpy.array_equal(result, expected)

    def test_qc_action_pad(self):
        '''
        Check that qc_action correctly applies the actions with padding.
        '''
        
        result = qc_action('Remove above reject',
                           main.pack_array(numpy.array([False, False, False, True, False, False])),
                           pad = 1)
        expected = [True, True, True, True, True, False]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove below reject',
                           main.pack_array(numpy.array([False, False, False, True, False, False])),
                           pad = 2)
        expected = [False, True, True, True, True, True]
        assert numpy.array_equal(result, expected)

        result = qc_action('Remove rejected levels',
                           main.pack_array(numpy.array([True, False, False, False, False, True])),
                           pad = 1)
        expected = [True, True, False, False, True, True]
        assert numpy.array_equal(result, expected)


