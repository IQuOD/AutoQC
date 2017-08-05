import util.main as main
import pandas, StringIO
import sys, psycopg2, pickle, StringIO, numpy, sqlite3, io
import numpy as np

def unpack_qc(value):
    'unpack a qc result from the db'

    try:
        qc = np.load(io.BytesIO(value))
    except:
        print 'failed to unpack qc data - check db for missing entries.'
        qc = np.zeros(1, dtype=bool)

    return qc

def summarize(levels):
    'given an array of level qc decisions, return true iff any of the levels are flagged'

    return numpy.any(levels)

def parse(results):
    'parse the raw pickled text of a per-level qc result, and return True if any levels are flagged'
    
    return results.apply(unpack_qc).apply(summarize)

if len(sys.argv) == 2:

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
    query += ' FROM ' + sys.argv[1]
    
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = ['Truth'] + testNames
    df[['Truth']] = df[['Truth']].apply(parse)
    df[testNames] = df[testNames].apply(parse)

    # summarize results
    print('%35s %7s %7s %7s %7s %7s' % ('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR')) 
    for test in testNames:
       tpr, fpr, fnr, tnr = main.calcRates(df[test].tolist(), df['Truth'].tolist())
       print('%35s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % (test, sum(df[test].tolist()), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))

else:

    print('Usage: python summarize-results.py databasetable')
