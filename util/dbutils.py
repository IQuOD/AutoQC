import io, math
import numpy
import pandas
import sqlite3
import util.main as main

def unpack_qc(value):
    'unpack a qc result from the db'

    try:
        qc = numpy.load(io.BytesIO(value), allow_pickle=True)
    except:
        print('failed to unpack qc data - check db for missing entries.')
        qc = numpy.zeros(1, dtype=bool)

    return qc

def summarize(levels):
    'given an array of level qc decisions, return true iff any of the levels are flagged'

    return numpy.any(levels)

def parse(results):
    'parse the raw pickled text of a per-level qc result, and return True if any levels are flagged'

    return results.apply(unpack_qc).apply(summarize)

def summarize_truth(levels):
    'given an array of originator qc decisions, return true iff any of the levels are flagged, ignoring t=99 levels'

    return numpy.sum( [not levels.mask[i] and (x==3 or x==4) for i, x in enumerate(levels)]) >= 1

def parse_truth(results):

    return results.apply(unpack_qc).apply(summarize_truth)

def get_n_levels_before_fail(results):

    nlevels = []
    for result in results:
        n = 0
        if type(result) is numpy.ndarray or type(result) is numpy.ma.core.MaskedArray or type(result) is list:
            qcresult = result
        else:
            qcresult = unpack_qc(result)
        for qc in qcresult:
            if qc == False:
                n += 1
            else:
                break
        nlevels.append(n)

    return nlevels

def get_reversed_n_levels_before_fail(results):

    nlevels = []
    for result in results:
        n = 0
        if type(result) is numpy.ndarray or type(result) is numpy.ma.core.MaskedArray or type(result) is list:
            qcresult = result
        else:
            qcresult = unpack_qc(result)
        for qc in qcresult[::-1]:
            if qc == False:
                n -= 1
            else:
                break
        
        nlevels.append(n)

    return nlevels

def check_for_fail(results):

    fails = []
    for result in results:
        answer = False
        if type(result) is numpy.ndarray or type(result) is numpy.ma.core.MaskedArray or type(result) is list:
            qcresult = result
        else:
            qcresult = unpack_qc(result)
        for qc in qcresult:
            if qc == True:
                answer = True
                break
        fails.append(answer)

    return fails

def unpack_qc_results(results):

    return [unpack_qc(result) for result in results] 

def qc_action(action, qc, pad=0):
    '''
    Applies action to the qc results with padding
    '''
    # Define results array.
    result = unpack_qc(qc)

    # Apply the action.
    if action == 'Remove above reject':
        nlevels = get_reversed_n_levels_before_fail([result])[0]
        if nlevels == 0:
            result[:] = True
        else:
            result[:nlevels] = True
    elif action == 'Remove below reject':
        nlevels = get_n_levels_before_fail([result])[0]
        if nlevels == 0:
            result[:] = True
        else:
            result[nlevels+1:] = True
    elif action == 'Remove profile':
        result[:] = check_for_fail([result])[0]
    elif action == 'Remove rejected levels':
        pass # Keep the original QC results.
    else:
        raise NameError('Unrecognised action: ' + action)
        
    # Add padding if required.
    if (pad > 0):
        resultorig = result.copy()
        for ipad, qcpad in enumerate(resultorig):
            if qcpad:
                ipadstart = max(0, ipad - pad)
                ipadend   = min(len(result), ipad + pad + 1)
                result[ipadstart:ipadend] = True

    # Return the result, which has True where levels should be removed
    # and False where levels should be kept.
    return result

def db_to_df(table,
             filter_on_wire_break_test=False, 
             filter_on_tests={},
             n_to_extract=numpy.iinfo(numpy.int32).max,
             applyparse=True,
             targetdb='iquod.db',
             pad=0, 
             XBTbelow=False):

    '''
    Reads the table from targetdb into a pandas dataframe.
    If filter_on_wire_break_test is True, the results from that test are used to exclude
         levels below a wire break from the test results and the wire break test is not returned.
    filter_on_tests is a generalised form of filter_on_wire_break and is used to exclude results; it takes a list of
         [testname, action], where levels failing <testname> are excluded towards the surface (if action is 'up'), towards depth (if action is 'down') and the whole profile deleted (if action is 'remove').
    Set n_to_extract to limit the number of rows extracted to the specified number.
    Set pad to remove extra levels around a fail to make sure that it is got rid of.
    Set XBTbelow to remove levels below an XBT fail.
    '''

    # what tests are available
    testNames = main.importQC('qctests')
    testNames.sort()

    # connect to database
    conn = sqlite3.connect(targetdb, isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT uid, truth'
    for test in testNames:
        query += ', ' + test.lower()
    query += ', probe FROM ' + table   
    query += ' WHERE uid IN (SELECT uid FROM ' + table + ' ORDER BY RANDOM() LIMIT ' + str(n_to_extract) + ')' 

    cur.execute(query)
    rawresults = cur.fetchall()
    
    # ensure XBT wire breaks handling is set up by adding it to the
    # filter_on_tests['Remove below reject'] group
    if filter_on_wire_break_test:
        if 'Remove below reject' in filter_on_tests.keys():
            if 'CSIRO_wire_break' not in filter_on_tests['Remove below reject']:
                filter_on_tests['Remove below reject'].append('CSIRO_wire_break')
        else:
            filter_on_tests['Remove below reject'] = ['CSIRO_wire_break']

    # Loop over the profiles, 1000 profiles at a time.
    sub  = 1000 # Number of profiles to process at a time.
    nsub = math.ceil(len(rawresults)/sub) # Number of batches of 1000 profiles there will be.
    df_final = None
    testNamesSave = testNames.copy()
    for i in range(nsub):
        # Define the start and end points of this batch of profiles and create a dataframe from them.
        istart = i * sub
        iend   = min((i + 1) * sub, len(rawresults))
        df = pandas.DataFrame(rawresults[istart:iend]).astype('bytes')
        df.columns = ['uid', 'Truth'] + testNamesSave + ['probe'] # Probe is needed for XBTbelow functionality.
        df = df.astype({'uid': 'int'})
        df = df.astype({'probe': 'float'})

        # todrop stores a set of profiles that are completely removed by any actions we apply.
        todrop = set()
        for action in filter_on_tests:
            # Check if the action requires any processing.
            if action == 'Optional' or action == 'At least one from group': continue

            # Loop over the tests that will have this action applied.
            for testname in filter_on_tests[action]:
            
                # Loop over the profiles, a.        
                for ip in range(len(df.index)):

                    # If XBTbelow is set, the Remove rejected levels action is replaced with
                    # Remove below reject for XBT profiles.
                    actiontoapply = action
                    if XBTbelow and (df['probe'][ip] == 2) and (action == 'Remove rejected levels'):
                        actiontoapply = 'Remove below reject'

                    # Use the qc_action function to apply the action.
                    applied = qc_action(actiontoapply,
                                        df[testname][ip],  
                                        pad)

                    # Apply the result of the action.
                    if numpy.count_nonzero(applied == False) == 0:
                        # Completely remove a profile if it has no valid levels after applying the action.
                        todrop.add(ip)
                    elif numpy.count_nonzero(applied == True) == 0:
                        # Nothing to do as there were no rejected levels.
                        pass
                    else:
                        for j in range(1, len(df.columns) - 1):
                            # Retain only the levels that passed testname.
                            qc = unpack_qc(df.iloc[ip, j])
                            qc = qc[applied == False]            
                            df.iat[ip, j] = main.pack_array(qc)

                del df[testname] # No need to keep this any longer.
                df.reset_index(inplace=True, drop=True)
        
        # Drop the profiles that no longer have any valid levels.        
        todrop = list(todrop)
        if len(todrop) > 0:
            df.drop(todrop, inplace=True)
        df.reset_index(inplace=True, drop=True)
        testNames = df.columns[2:-1].values.tolist()
        
        # Apply the parse if required.
        if applyparse:
            df[['Truth']] = df[['Truth']].apply(parse_truth)
            df[testNames] = df[testNames].apply(parse)

        # Keep the results.
        if i == 0:
            df_final = df
        else:
            df_final = pandas.concat([df_final, df])
    
    # Remove the probe column before returning.
    del df_final['probe']
    return df_final.reset_index(drop=True)
    
def retrieve_existing_qc_result(test, uid, table='iquod', db='iquod.db'):
    '''
    Extracts QC results from the d:
    test  - the QC check to get results for.
    uid   - the profile unique ID to get results for.
    table - the database table for the profile.
    db    - the name of the database file.
    '''

    # The query below has three possible outcomes:
    # 1) Returns a NoneType object if the test name does not exist. This is
    #    caught as an error when the len(qc_log) command is run which then fails
    #    in the except structure.
    # 2) Returns an empty list if the profile does not exist in the database.
    #    The code passes the try/except commands and fails at the end.
    # 3) Returns a list containing either None if the QC results haven't been
    #    stored or the QC results themselves, which are then returned.
    
    query = 'SELECT {} FROM {} WHERE uid = {};'.format(test, table, uid)
    qc_log = main.dbinteract(query, targetdb=db)
    try:
        if len(qc_log) > 0:
            qc_log = main.unpack_row(qc_log[0])
            return qc_log[0]
    except:
        print('***** Test name does not seem to exist in the database')
        print(query)
        print(qc_log)
        raise

    # If this point has been reached it means that the profile does not exist.
    print('***** Profile does not seem to exist in the database')
    print(query)
    print(qc_log)
    raise
    

