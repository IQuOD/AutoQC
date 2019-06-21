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

    print('{0:35s} {1:7s} {2:7s} {3:7s} {4:7s} {5:7s}'.format('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR'))
    for test in testNames:
       tpr, fpr, fnr, tnr = main.calcRates(df[test].tolist(), df['Truth'].tolist())
       print('{0:35s} {1:7d} {2:6.1f}{3:1s} {4:6.1f}{5:1s} {6:6.1f}{7:1s} {8:6.1f}{9:1s}'.format(test, sum(df[test].tolist()), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))

else:

    print('Usage: python summarize-results.py databasetable')
