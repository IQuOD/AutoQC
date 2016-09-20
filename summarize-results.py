import util.main as main
import pandas, StringIO
import sys, psycopg2, pickle, StringIO, numpy

def unpickle(value):
    'unpickle a text encoding of a something pickled to the database'

    return pickle.load(StringIO.StringIO(value))

def summarize(levels):
    'given an array of level qc decisions, return true iff any of the levels are flagged'

    return numpy.any(levels)

def parse(results):
    'parse the raw pickled text of a per-level qc result, and return True if any levels are flagged'

    return results.apply(unpickle).apply(summarize)

if len(sys.argv) == 2:

    # what tests are available
    testNames = main.importQC('qctests')
    testNames.sort()

    # connect to database
    conn = psycopg2.connect("dbname='root' user='root'")
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
    df[['Truth']] = df[['Truth']].astype('bool')
    df[testNames] = df[testNames].apply(parse)

    # summarize results
    print('%35s %7s %7s %7s %7s %7s' % ('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR')) 
    for test in testNames:
        tpr, fpr, fnr, tnr = main.calcRates(df[test].tolist(), df['Truth'].tolist())
        print('%35s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % (test, sum(df[test].tolist()), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))

else:

    print('Usage: python summarize-results.py databasetable')
