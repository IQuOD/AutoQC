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
        answer = False
        for qc in unpack_qc(result):
            if qc == True:
                answer = True
                break
        fails.append(answer)

    return fails

def unpack_qc_results(results):

    return [unpack_qc(result) for result in results] 

def db_to_df(table,
             filter_on_wire_break_test=False, 
             filter_on_tests={},
             n_to_extract=numpy.iinfo(numpy.int32).max,
             applyparse=True,
             targetdb='iquod.db'):

    '''
    Reads the table from targetdb into a pandas dataframe.
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
    conn = sqlite3.connect(targetdb, isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT uid, truth'
    for test in testNames:
        query += ', ' + test.lower()
    query += ' FROM ' + table   
    query += ' WHERE uid IN (SELECT uid FROM ' + table + ' ORDER BY RANDOM() LIMIT ' + str(n_to_extract) + ')' 

    cur.execute(query)
    rawresults = cur.fetchall()

    sub = 1000
    df_final = None
    for i in range(math.ceil(len(rawresults)/sub)):
        df = pandas.DataFrame(rawresults[i*sub:(i+1)*sub]).astype('bytes')
        df.columns = ['uid', 'Truth'] + testNames
        df = df.astype({'uid': 'int'})
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

        todrop = set()
        for action in filter_on_tests:
            # Check if the action is relevant.
            if action == 'Optional' or action == 'At least one from group': continue

            # Initialise variables.
            nlevels   = -1
            outcomes  = False
            qcresults = []
            for testname in filter_on_tests[action]:
                for i in range(0, len(df.index)):
                    if action == 'Remove above reject':
                        nlevels = get_reversed_n_levels_before_fail([df[testname][i]])[0]
                    elif action == 'Remove below reject':
                        nlevels = get_n_levels_before_fail([df[testname][i]])[0]
                    elif action == 'Remove profile':
                        outcomes = check_for_fail([df[testname][i]])[0]
                    elif action == 'Remove rejected levels':
                        qcresults = unpack_qc_results([df[testname][i]])[0]
                    else:
                        raise NameError('Unrecognised action: ' + action)

                    if (((action == 'Remove above reject' or action == 'Remove below reject') and nlevels == 0) or
                        (action == 'Remove profile' and outcomes == True) or
                        (action == 'Remove rejected levels' and numpy.count_nonzero(qcresults == False) == 0)):
                        # Completely remove a profile if it has no valid levels or if it
                        # has a fail and the action is to remove.
                        todrop.add(i)
                    elif (action != 'Remove profile'):
                        for j in range(1, len(df.columns)):
                            # Retain only the levels that passed testname.
                            # Some QC tests may return only one value so check for this.
                            qc = unpack_qc(df.iloc[i, j])
                            if len(qc) > 1:
                                if action == 'Remove above reject':
                                    qc = qc[nlevels:]
                                elif action == 'Remove below reject':
                                    qc = qc[:nlevels] 
                                elif action == 'Remove rejected levels':
                                    qc = qc[qcresults == False]            
                                df.iat[i, j] = main.pack_array(qc)

                del df[testname] # No need to keep this any longer.
                df.reset_index(inplace=True, drop=True)
                
        todrop = list(todrop)
        if len(todrop) > 0:
            df.drop(todrop, inplace=True)
        df.reset_index(inplace=True, drop=True)
        testNames = df.columns[2:].values.tolist()
        if applyparse:
            df[['Truth']] = df[['Truth']].apply(parse_truth)
            df[testNames] = df[testNames].apply(parse)

        if i == 0:
            df_final = df
        else:
            df_final = pandas.concat([df_final, df])

    return df_final.reset_index(drop=True)
