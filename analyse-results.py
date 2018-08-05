import csv
import json, pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
from util import dbutils, main

def read_qc_groups(filename='qctest_groups.csv'):
    # Read a csv file containing information on QC test groups.
    # The program returns a dictionary containing the information 
    # from csv file.

    csvfile = open(filename) 
    groupinfo = csv.reader(csvfile)

    # Create empty lists for each type of group.
    groupdefinition = {'Remove above reject':[],
                       'Remove below reject':[],
                       'Remove rejected levels':[],
                       'Remove profile':[],
                       'Optional':[],
                       'At least one from group':{}}

    # Fill out the lists.
    for i, spec in enumerate(groupinfo):
        if i == 0: continue # Miss the header line.
        if spec[1] in groupdefinition:
            # For the 'at least one from group' rule we maintain lists of 
            # the tests in each group.
            if spec[1] == 'At least one from group':
                if spec[0] in groupdefinition[spec[1]]:
                    groupdefinition[spec[1]][spec[0]].append(spec[2])
                else:
                    groupdefinition[spec[1]][spec[0]] = [spec[2]]
            else:
                # Other rules have a list of the tests that fall into them.
                groupdefinition[spec[1]].append(spec[2])
        else:
            raise NameError('Rule not recognised: ', spec)

    csvfile.close()

    return groupdefinition

def find_roc(table, 
             filter_on_wire_break_test=False,
             filter_from_file_spec=True,
             enforce_types_of_check=True,
             n_profiles_to_analyse=np.iinfo(np.int32).max,
             n_combination_iterations=0, 
             with_reverses=False,
             effectiveness_threshold=2.0,
             improve_threshold=1.0, 
             verbose=True, 
             plot_roc=True,
             write_roc=True):
    '''
    Generates a ROC curve from the database data in table by maximising the gradient
    of the ROC curve. It will combine different tests together and invert the results
    of tests if requested.

    filter_on_wire_break_test - filter out the impact of XBT wire breaks from results.
    filter_from_file_spec - use specification from file to choose filtering.
    enforce_types_of_check - use specification from file on particular types of checks to use.
    n_profiles_to_analyse - restrict the number of profiles extracted from the database.
    n_combination_iterations - AND tests together; restricted to max of 2 as otherwise
                               number of tests gets very large.
    with_reverses - if True, a copy of each test with inverted results is made.
    effectiveness_threshold - test combinations with TPR/FPR less than this are not used when 
                              making the ROC curve. If enforcing types of check tests with 
                              TPR/FPR less than effectiveness_threshold are use and a warning
                              printed to screen. 
    improve_threshold - ignores tests if they do not results in a change in true positive 
                        rate (in %) of at least this amount.
    verbose - if True, will print a lot of messages to screen.
    plot_roc - if True, will save an image of the ROC to roc.png.
    write_roc - if True, will save the ROC data to roc.json.
    '''

    # Read QC test specifications if required.
    groupdefinition = {}
    if filter_from_file_spec or enforce_types_of_check:
        groupdefinition = read_qc_groups()

    # Read data from database into a pandas data frame.
    df = dbutils.db_to_df(sys.argv[1],
                          filter_on_wire_break_test = filter_on_wire_break_test,
                          filter_on_tests = groupdefinition,
                          n_to_extract = n_profiles_to_analyse)

    # drop nondiscriminating tests
    nondiscrim = []
    cols = list(df.columns)
    for c in cols:
        if len(pandas.unique(df[c])) == 1:
            nondiscrim.append(c)
            if verbose: print c + ' is nondiscriminating and will be removed'
    cols = [t for t in cols if t not in nondiscrim]
    df = df[cols]
    print list(df)
    testNames = df.columns[2:].values.tolist()

    if verbose:
        print 'Number of profiles is: ', len(df.index)
        print 'Number of quality checks to process is: ', len(testNames)

    # mark chosen profiles as part of the training set 
    all_uids = main.dbinteract('SELECT uid from ' + sys.argv[1] + ';')
    for uid in all_uids:
        uid = uid[0]
        is_training = int(uid in df['uid'].astype(int).as_matrix())
        query = "UPDATE " + sys.argv[1] + " SET training=" + str(is_training) + " WHERE uid=" + str(uid) + ";"
        main.dbinteract(query)

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
    if verbose: print 'Number of quality checks after adding reverses and removing zero TPR was: ', len(names)

    # Create storage to hold the roc curve.
    cumulative = truth.copy()
    cumulative[:] = False
    currenttpr    = 0.0
    currentfpr    = 0.0
    r_fprs        = [] # The false positive rate for each ROC point.
    r_tprs        = [] # True positive rate for each ROC point.
    testcomb      = [] # The QC test that was added at each ROC point.
    groupsel      = [] # Set to True if the ROC point was from an enforced group.

    # Pre-select some tests if required.
    if enforce_types_of_check:
        if verbose: print 'Enforcing types of checks'
        for key in groupdefinition['At least one from group']:
            if verbose: print '  Selecting from group: ' + key
            bestchoice = ''
            bestdist   = 100.0**2 + 100.0**2
            besti      = -1
            for testname in groupdefinition['At least one from group'][key]:
                # Need to check that the test exists - it may have been removed
                # if it was non-discriminating.
                if testname in names:
                    for itest, name in enumerate(names):
                        if name == testname: 
                            tpr = tprs[itest]
                            fpr = fprs[itest]                    
                            newdist = (100.0 - tpr)**2 + fpr**2
                            print '    ', tpr, fpr, newdist, bestdist, testname
                            if newdist == bestdist:
                                if verbose:
                                    print '  ' + bestchoice + ' and ' + testname + ' have the same results and the first is kept'
                            elif newdist < bestdist:
                                bestchoice = testname
                                bestdist   = newdist
                                besti      = itest
                else:
                    if verbose: print '    ' + testname + ' not found and so was skipped'
            assert bestchoice != '', '    Error, did not make a choice in group ' + key
            if verbose: print '  ' + bestchoice + ' was selected'
            if fprs[besti] > 0:
                if tprs[besti] / fprs[besti] < effectiveness_threshold:
                    print 'WARNING - ' + bestchoice + ' TPR / FPR is below the effectiveness threshold: ', tprs[besti] / fprs[besti]
            cumulative = np.logical_or(cumulative, tests[besti])
            currenttpr, currentfpr, fnr, tnr = main.calcRates(cumulative, truth)
            testcomb.append(names[besti])
            r_fprs.append(currentfpr)
            r_tprs.append(currenttpr)
            groupsel.append(True)
            # Once a test has been added, it can be deleted so that it is not considered again.
            del names[besti]
            del tests[besti]
            del fprs[besti]
            del tprs[besti]
            print 'ROC point from enforced group: ', currenttpr, currentfpr, testcomb[-1]

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
                if fpr > 0:
                    ratio = effectiveness_threshold + 1
                else:
                    ratio = tpr / fpr
                if tpr > 0.0 and ratio >= effectiveness_threshold:
                    tests.append(results)
                    tprs.append(tpr)
                    fprs.append(fpr)
                    names.append(newname)
    if verbose: print 'Completed generation of tests, now constructing roc from number of tests: ', len(names)         

    # Create roc by keep adding tests in order of ratio of tpr/fpr change to get the highest
    # gradient in the roc curve.
    keepgoing = True
    used      = np.zeros(len(names), dtype=bool)
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
            groupsel.append(False)
            print 'ROC point: ', currenttpr, currentfpr, names[besti]

    if plot_roc:
        plt.plot(r_fprs, r_tprs, 'k')
        for i in range(len(r_fprs)):
            if groupsel[i]:
                colour = 'r'
            else:
                colour = 'b'
            plt.plot(r_fprs[i], r_tprs[i], colour + 'o')
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
        r['groupsel'] = groupsel
        json.dump(r, f)
        f.close()

if __name__ == '__main__':

    # python analyse-results.py <database table name> <number of profiles to extract> <flag to run combinations and no enforce of groups - can be any value>

    if len(sys.argv) == 3:
        find_roc(sys.argv[1], n_profiles_to_analyse=sys.argv[2])
    elif len(sys.argv) == 4:
        find_roc(sys.argv[1], n_profiles_to_analyse=sys.argv[2], enforce_types_of_check=False, n_combination_iterations=1)
    else:
        print 'Usage - python analyse_results.py tablename <number of profiles to train ROC curve on> <optional character or number to indicate that we run one test combination iteration and no enforcing of groups>'

