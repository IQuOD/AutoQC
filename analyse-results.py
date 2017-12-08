import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
from util import dbutils, main

def find_roc(table, 
             filter_on_wire_break_test=True,
             n_profiles_to_analyse=np.iinfo(np.int32).max,
             n_combination_iterations=2, 
             with_reverses=False,
             improve_threshold=1.0, 
             verbose=True, 
             plot_roc=True,
             write_roc=True):
    '''
    Generates a ROC curve from the database data in table by maximising the gradient
    of the ROC curve. It will combine different tests together and invert the results
    of tests if requested.

    filter_on_wire_break_test - filter out the impact of XBT wire breaks from results.
    n_profiles_to_analyse - restrict the number of profiles extracted from the database.
    n_combination_iterations - AND tests together; restricted to max of 2 as otherwise
                               number of tests gets very large.
    with_reverses - if True, a copy of each test with inverted results is made.
    improve_threshold - ignores tests if they do not results in a change in true positive 
                        rate (in %) of at least this amount.
    verbose - if True, will print a lot of messages to screen.
    plot_roc - if True, will save an image of the ROC to roc.png.
    write_roc - if True, will save the ROC data to roc.json.
    '''

    # Read data from database into a pandas data frame.
    df        = dbutils.db_to_df(sys.argv[1], 
                                 filter_on_wire_break_test=filter_on_wire_break_test,
                                 n_to_extract=n_profiles_to_analyse)
    testNames = df.columns[1:].values.tolist()
    if verbose: 
        print 'Number of profiles from database was: ', len(df.index)
        print 'Number of quality checks from database was: ', len(testNames)

    # Convert to numpy structures and make inverse versions of tests if required.
    # Any test with true positive rate of zero is discarded.
    truth = df['Truth'].as_matrix()
    tests = []
    names = []
    tprs  = []
    fprs  = []
    if with_reverses:
        reverselist = [False, True]
    else:
        reverselist = [False]
    for i, testname in enumerate(testNames):
        for reversal in reverselist:
            results = df[testname].as_matrix() != reversal
            tpr, fpr, fnr, tnr = main.calcRates(results, truth)
            if tpr > 0.0: 
                tests.append(results)
                if reversal:
                    addtext = 'r'
                else:
                    addtext = ''
                names.append(addtext + testname)
                tprs.append(tpr)
                fprs.append(fpr)
    del df # No further need for the data frame.
    if verbose: print 'Number of quality checks after reverses and removing zero TPR was: ', len(names)

    # Make combinations of the single checks and store.
    assert n_combination_iterations <= 2, 'Setting n_combination_iterations > 2 results in a very large number of combinations'
    if verbose: print 'Starting construction of combinations with number of iterations: ', n_combination_iterations
    for its in range(n_combination_iterations):
        ntests = len(names)
        for i in range(ntests - 1):
            if verbose: print 'Processing iteration ', its + 1, ' out of ', n_combination_iterations, ' step ', i + 1, ' out of ', ntests - 1, ' with number of tests now ', len(names)
            for j in range(i + 1, ntests):
                # Create the name for this combination.
                newname = ('&').join(sorted((names[i] + '&' + names[j]).split('&')))
                if newname in names: continue # Do not keep multiple copies of the same combination.

                results = np.logical_and(tests[i], tests[j])
                tpr, fpr, fnr, tnr = main.calcRates(results, truth)
                if tpr > 0.0: 
                    tests.append(results)
                    tprs.append(tpr)
                    fprs.append(fpr)
                    names.append(newname)
    if verbose: print 'Completed generation of tests, now constructing roc from number of tests: ', len(names)

    # Create storage to hold the roc curve.
    cumulative = truth.copy()
    cumulative[:] = False
    currenttpr    = 0.0
    currentfpr    = 0.0
    used          = np.zeros(len(names), dtype=bool) 
    r_fprs    = []
    r_tprs    = []

    # Create roc by keep adding tests in order of ratio of tpr/fpr change to get the highest
    # gradient in the roc curve.
    keepgoing = True
    used      = np.zeros(len(names), dtype=bool)
    testcomb  = []
    while keepgoing:
        keepgoing = False
        besti     = -1
        bestratio = 0.0
        bestncomb = 100000
        bestdtpr  = 0
        bestdfpr  = 100000
        for i in range(len(names)):
            if used[i]: continue
            cumulativenew = np.logical_or(cumulative, tests[i])
            tpr, fpr, fnr, tnr = main.calcRates(cumulativenew, truth)
            dtpr = tpr - currenttpr
            dfpr = max(fpr - currentfpr, 0.1 / len(cumulative)) # In case of 0 change in fpr.
            ratio = dtpr / dfpr
            newbest = False
            if ratio >= bestratio and dtpr >= improve_threshold and dtpr > 0.0:
                # If ration is better than found previously, use it else if it is
                # the same then decide if to use it or not.
                if ratio > bestratio:
                    newbest = True
                elif dtpr >= bestdtpr:
                    if dtpr > bestdtpr:
                        newbest = True
                    elif len(names[i].split('&')) < bestncomb:
                        newbest = True
            if newbest:
                besti     = i
                bestratio = ratio
                bestncomb = len(names[i].split('&'))
                bestdtpr  = dtpr
                bestdfpr  = dfpr
        if besti >= 0:
            keepgoing = True
            used[besti] = True
            cumulative = np.logical_or(cumulative, tests[besti])
            currenttpr, currentfpr, fnr, tnr = main.calcRates(cumulative, truth)
            testcomb.append(names[besti])
            r_fprs.append(currentfpr)
            r_tprs.append(currenttpr)
            print 'ROC point: ', currenttpr, currentfpr, names[besti]

    if plot_roc:
        plt.plot(r_fprs, r_tprs)
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.xlabel('False positive rate (%)')
        plt.ylabel('True positive rate (%)')
        plt.savefig('roc.png')
        plt.close()

    if write_roc:
        f = open('roc.json', 'w')
        r = {}
        r['tpr'] = r_tprs
        r['fpr'] = r_fprs
        r['tests'] = testcomb
        json.dump(r, f)
        f.close()

if __name__ == '__main__':

    if len(sys.argv) == 2:
        find_roc(sys.argv[1])
    elif len(sys.argv) == 3:
        find_roc(sys.argv[1], n_profiles_to_analyse=sys.argv[2])
    else:
        print 'Usage - python analyse_results.py tablename [number of profiles to read from database]'
         
