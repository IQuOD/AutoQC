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

    return numpy.sum([x >= 3 and x < 99 for x in levels ]) >= 1

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

def db_to_df(table,
             filter_on_wire_break_test=False, 
             n_to_extract=numpy.iinfo(numpy.int32).max):

    '''
    Reads the table from iquod.db into a pandas dataframe.
    If filter_on_wire_break_test is True, the results from that test are used to exclude
         levels below a wire break from the test results and the wire break test is not returned.
    Set n_to_extract to limit the number of rows extracted to the specified number.
    '''

    # what tests are available
    testNames = main.importQC('qctests')
    testNames.sort()

    # connect to database
    conn = sqlite3.connect('iquod.db', isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT truth'
    for test in testNames:
        query += ', ' + test.lower()
    query += ' FROM ' + table
    query += ' LIMIT ' + str(n_to_extract)    

    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = ['Truth'] + testNames

    if filter_on_wire_break_test:
        nlevels = get_n_levels_before_fail(df['CSIRO_wire_break'])
        del df['CSIRO_wire_break'] # No use for this now.
        testNames = df.columns[1:].values.tolist()
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                qc = unpack_qc(df.iloc[i, j])
                # Some QC tests may return only one value so check for this.
                if len(qc) > 1:
                    qc = qc[:nlevels[i]]
                df.iat[i, j] = main.pack_array(qc)

    df[['Truth']] = df[['Truth']].apply(parse_truth)
    df[testNames] = df[testNames].apply(parse)

    return df
