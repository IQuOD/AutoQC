import sys
import util.dbutils as dbutils
import util.main as main

'''
Prints a simple summary of true and false, postive and negative rates.

Usage: python summarize-results.py databasetable
'''

if len(sys.argv) == 2:

    df        = dbutils.db_to_df(sys.argv[1])
    testNames = df.columns[1:].values.tolist()

    print('%35s %7s %7s %7s %7s %7s' % ('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR')) 
    for test in testNames:
       tpr, fpr, fnr, tnr = main.calcRates(df[test].tolist(), df['Truth'].tolist())
       print('%35s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % (test, sum(df[test].tolist()), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))

else:

    print('Usage: python summarize-results.py databasetable')
