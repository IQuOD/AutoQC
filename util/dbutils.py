import io
import numpy
import pandas
import sqlite3
import util.main as main

def unpack_qc(value):
    'unpack a qc result from the db'

    try:
        qc = numpy.load(io.BytesIO(value))
    except:
        print 'failed to unpack qc data - check db for missing entries.'
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

    return numpy.sum( [not levels.mask[i] and x>=3 and x<99 for i, x in enumerate(levels)]) >= 1

def parse_truth(results):

    return results.apply(unpack_qc).apply(summarize_truth)

def get_n_levels_before_fail(results):

    nlevels = []
    for result in results:
        n = 0
        for qc in unpack_qc(result):
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
        for qc in unpack_qc(result)[::-1]:
            if qc == False:
                n -= 1
            else:
                break
        
        nlevels.append(n)

    return nlevels

def check_for_fail(results):

    fails = []
    for result in results:
        result = False
        for qc in unpack_qc(result):
            if qc == True:
                result = True
                break
        fails.append(result)

    return fails

def unpack_qc_results(results):

    return [unpack_qc(result) for result in results] 

def db_to_df(table,
             filter_on_wire_break_test=False, 
             filter_on_tests=[],
             n_to_extract=numpy.iinfo(numpy.int32).max):

    '''
    Reads the table from iquod.db into a pandas dataframe.
    If filter_on_wire_break_test is True, the results from that test are used to exclude
         levels below a wire break from the test results and the wire break test is not returned.
    filter_on_tests is a generalised form of filter_on_wire_break and is used to exclude results; it takes a list of
         [testname, action], where levels failing <testname> are excluded towards the surface (if action is 'up'), towards depth (if action is 'down') and the whole profile deleted (if action is 'remove').
    Set n_to_extract to limit the number of rows extracted to the specified number.
    '''

    # what tests are available
    testNames = main.importQC('qctests')
    testNames.sort()

    # connect to database
    conn = sqlite3.connect('iquod.db', isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT uid, truth'
    for test in testNames:
        query += ', ' + test.lower()
    query += ' FROM ' + table   
    query += ' WHERE uid IN (SELECT uid FROM ' + table + ' ORDER BY RANDOM() LIMIT ' + str(n_to_extract) + ')' 

    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = ['uid', 'Truth'] + testNames

    if filter_on_wire_break_test:
        nlevels = get_n_levels_before_fail(df['CSIRO_wire_break'])
        del df['CSIRO_wire_break'] # No use for this now.
        testNames = df.columns[2:].values.tolist()
        for i in range(len(df.index)):
            for j in range(1, len(df.columns)):
                qc = unpack_qc(df.iloc[i, j])
                # Some QC tests may return only one value so check for this.
                if len(qc) > 1:
                    qc = qc[:nlevels[i]]
                df.iat[i, j] = main.pack_array(qc)

    for ftest in filter_on_tests:
        testname = ftest[0]
        action   = ftest[1]

        for i in range(0, len(df.index), -1):

            if action == 'removeabove':
                nlevels = get_reversed_n_levels_before_fail([df[testname][i]])[0]
            elif action == 'removebelow':
                nlevels = get_n_levels_before_fail([df[testname][i]])[0]
            elif action == 'removeprofile':
                outcomes = check_for_fail([df[testname][i]])[0]
            elif action == 'removelevels':
                qcresults = unpack_qc_results([df[testname][i]])[0]
            else:
                raise NameError('Unrecognised action: ' + action)

            if (((action == 'removeabove' or action == 'removebelow') and nlevels[i] == 0) or
               (action == 'removeprofile' and outcomes[i] == True) or
               (action == 'removelevels' and np.count_nonzero(qcresults == False) == 0)):
                # Completely remove a profile if it has no valid levels or if it
                # has a fail and the action is to remove.
                df.drop(df.index[i])
            elif (action != 'removeprofile'):
                for j in range(1, len(df.columns)):
                    # Retain only the levels that passed testname.
                    # Some QC tests may return only one value so check for this.
                    qc = unpack_qc(df.iloc[i, j])
                    if len(qc) > 1:
                        if action == 'removeabove':
                            qc = qc[nlevels[i]:]
                        elif action == 'removebelow':
                            qc = qc[:nlevels[i]] 
                        elif action == 'removelevels':
                            qc = qc[qcresults == False]            
                        df.iat[i, j] = main.pack_array(qc)

        del df[testname] # No need to keep this any longer.

    testNames = df.columns[2:].values.tolist()
    df[['Truth']] = df[['Truth']].apply(parse_truth)
    df[testNames] = df[testNames].apply(parse)

    return df
