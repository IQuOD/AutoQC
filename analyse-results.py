import csv, getopt, json, pandas, sys, ast
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
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

def return_cost(costratio, tpr, fpr):
    # Return cost function.
    # Inputs are:
    #     costratio - 2 element iterable used to define the cost function; roughly 
    #                 they define the minimum required gradient of the ROC curve
    #                 with the first giving the gradient at the start, the second
    #                 the gradient at the end. Suggested values: to get a compromise
    #                 set of QC tests, define costratio = [2.5, 1.0]; to get a 
    #                 conservative set of QC tests, define costratio = [10.0, 10.0].
    #     tpr       - True positive rate to get the cost for.
    #     fpr       - False positive rate to get the cost for.
    # Returns: the cost function value.
    costratio1 = costratio[0]
    costratio2 = costratio[1]
    theta1 = np.arctan(costratio1)
    theta2 = np.arctan(costratio2)
    cost1 = (100.0 - tpr) * np.cos(theta1) + fpr * np.sin(theta1)
    cost2 = (100.0 - tpr) * np.cos(theta2) + fpr * np.sin(theta2)
    cost  = (100.0 - tpr) / 100.0 * cost1 + tpr / 100.0 * cost2
    return cost

def find_roc(table,
             targetdb,
             costratio=[2.5, 1.0],
             filter_on_wire_break_test=False,
             filter_from_file_spec=True,
             enforce_types_of_check=True,
             n_profiles_to_analyse=np.iinfo(np.int32).max,
             n_combination_iterations=0, 
             with_reverses=False,
             effectiveness_ratio=2.0,
             improve_threshold=1.0, 
             verbose=True, 
             plot_roc=True,
             write_roc=True,
             mark_training=False):
    '''
    Generates a ROC curve from the database data in table by maximising the gradient
    of the ROC curve. It will combine different tests together and invert the results
    of tests if requested.

    costratio - two element iterable that defines how the ROC curve is developed. Higher 
                numbers gives a ROC curve with lower false rates; the two elements allows
                control over the shape of the ROC curve near the start and end. E.g. [2.5, 1.0].
    filter_on_wire_break_test - filter out the impact of XBT wire breaks from results.
    filter_from_file_spec - use specification from file to choose filtering.
    enforce_types_of_check - use specification from file on particular types of checks to use.
    n_profiles_to_analyse - restrict the number of profiles extracted from the database.
    n_combination_iterations - AND tests together; restricted to max of 2 as otherwise
                               number of tests gets very large.
    with_reverses - if True, a copy of each test with inverted results is made.
    effectiveness_ratio - will give a warning if TPR / FPR is less than this value.
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
    df = dbutils.db_to_df(table = table,
                          targetdb = targetdb,
                          filter_on_wire_break_test = filter_on_wire_break_test,
                          filter_on_tests = groupdefinition,
                          n_to_extract = n_profiles_to_analyse,
                          pad=2, 
                          XBTbelow=True)

    # Drop nondiscriminating tests
    nondiscrim = []
    cols = list(df.columns)
    for c in cols:
        if len(pandas.unique(df[c])) == 1:
            nondiscrim.append(c)
            if verbose: print(c + ' is nondiscriminating and will be removed')
    cols = [t for t in cols if t not in nondiscrim]
    df = df[cols]
    print(list(df))
    testNames = df.columns[2:].values.tolist()

    if verbose:
        print('Number of profiles is: ', len(df.index))
        print('Number of quality checks to process is: ', len(testNames))

    # mark chosen profiles as part of the training set 
    all_uids = main.dbinteract('SELECT uid from ' + table + ';', targetdb=targetdb)
    if mark_training:
        for uid in all_uids:
            uid = uid[0]
            is_training = int(uid in df['uid'].astype(int).to_numpy())
            query = "UPDATE " + table + " SET training=" + str(is_training) + " WHERE uid=" + str(uid) + ";"
            main.dbinteract(query, targetdb=targetdb)

    # Convert to numpy structures and make inverse versions of tests if required.
    # Any test with true positive rate of zero is discarded.
    truth = df['Truth'].to_numpy()
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
            results = df[testname].to_numpy() != reversal
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
    if verbose: print('Number of quality checks after adding reverses and removing zero TPR was: ', len(names))

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
        if verbose: print('Enforcing types of checks')
        while len(groupdefinition['At least one from group']) > 0:
            bestchoice = ''
            bestgroup  = ''
            bestdist   = np.sqrt(100.0**2 + 100.0**2)
            besti      = -1
            for key in groupdefinition['At least one from group']:
                for testname in groupdefinition['At least one from group'][key]:
                    # Need to check that the test exists - it may have been removed
                    # if it was non-discriminating.
                    if testname in names:
                        for itest, name in enumerate(names):
                            if name == testname: 
                                cumulativenew = np.logical_or(cumulative, tests[itest])
                                tpr, fpr, fnr, tnr = main.calcRates(cumulativenew, truth)
                                newdist = return_cost(costratio, tpr, fpr)
                                print('    ', tpr, fpr, newdist, bestdist, testname)
                                if newdist == bestdist:
                                    if verbose:
                                        print('  ' + bestchoice + ' and ' + testname + ' have the same results and the first is kept')
                                elif newdist < bestdist:
                                    bestchoice = testname
                                    bestdist   = newdist
                                    besti      = itest
                                    bestgroup  = key
                    else:
                        if verbose: print('    ' + testname + ' not found and so was skipped')
            if bestchoice == '':
                print('WARNING no suitable tests in group "' + key + '", skipping')
                del groupdefinition['At least one from group'][key]
            else:
                if verbose: print('  ' + bestchoice + ' was selected from group ' + bestgroup)
                if fprs[besti] > 0:
                    if tprs[besti] / fprs[besti] < effectiveness_ratio:
                        print('WARNING - ' + bestchoice + ' TPR / FPR is below the effectiveness ratio limit: ', tprs[besti] / fprs[besti], effectiveness_ratio)
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
                del groupdefinition['At least one from group'][bestgroup]
                print('ROC point from enforced group: ', currenttpr, currentfpr, testcomb[-1], bestgroup)

    # Make combinations of the single checks and store.
    assert n_combination_iterations <= 2, 'Setting n_combination_iterations > 2 results in a very large number of combinations'
    if verbose: print('Starting construction of combinations with number of iterations: ', n_combination_iterations)
    for its in range(n_combination_iterations):
        ntests = len(names)
        for i in range(ntests - 1):
            if verbose: print('Processing iteration ', its + 1, ' out of ', n_combination_iterations, ' step ', i + 1, ' out of ', ntests - 1, ' with number of tests now ', len(names))
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
    if verbose: print('Completed generation of tests, now constructing roc from number of tests: ', len(names))

    # Create roc.
    used      = np.zeros(len(names), dtype=bool)
    overallbest = return_cost(costratio, tpr, fpr)
    keepgoing = True
    while keepgoing:
        keepgoing = False
        besti     = -1
        bestcost  = overallbest
        bestncomb = 100000
        bestdtpr  = 0
        bestdfpr  = 100000
        for i in range(len(names)):
            if used[i]: continue
            cumulativenew = np.logical_or(cumulative, tests[i])
            tpr, fpr, fnr, tnr = main.calcRates(cumulativenew, truth)
            dtpr               = tpr - currenttpr
            dfpr               = fpr - currentfpr
            newcost            = return_cost(costratio, tpr, fpr) 
            newbest            = False
            if newcost <= bestcost and dtpr >= improve_threshold and dtpr > 0.0:
                # If cost is better than found previously, use it else if it is
                # the same then decide if to use it or not.
                if newcost < bestcost:
                    newbest = True
                elif dtpr >= bestdtpr:
                    if dtpr > bestdtpr:
                        newbest = True
                    elif len(names[i].split('&')) < bestncomb:
                        newbest = True
                if newbest:
                    besti     = i
                    bestcost  = newcost
                    bestncomb = len(names[i].split('&'))
                    bestdtpr  = dtpr
                    bestdfpr  = dfpr
        if besti >= 0:
            keepgoing   = True
            used[besti] = True
            overallbest = bestcost
            cumulative  = np.logical_or(cumulative, tests[besti])
            currenttpr, currentfpr, fnr, tnr = main.calcRates(cumulative, truth)
            testcomb.append(names[besti])
            r_fprs.append(currentfpr)
            r_tprs.append(currenttpr)
            groupsel.append(False)
            print('ROC point: ', currenttpr, currentfpr, names[besti], overallbest)

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
        plt.savefig(plot_roc)
        plt.close()

    if write_roc:
        f = open(write_roc, 'w')
        r = {}
        r['tpr'] = r_tprs
        r['fpr'] = r_fprs
        r['tests'] = testcomb
        r['groupsel'] = groupsel
        json.dump(r, f)
        f.close()

def find_roc_ordered(table,
                     targetdb,
                     costratio=[2.5, 1.0],
                     n_profiles_to_analyse=np.iinfo(np.int32).max,
                     improve_threshold=1.0, 
                     verbose=True, 
                     plot_roc=True,
                     write_roc=True,
                     levelbased=False,
                     mark_training=False):
    '''
    Finds optimal tests to include in a QC set.
    table - the database table to read;
    targetdb - the datable file;
    n_profiles_to_analyse - how many profiles to read from the database;
    improve_threshold - how much improvement in true positive rate is needed
                        for a test to be accepted once all groups have been done;
    verbose - controls whether messages on progress are output;
    plot_roc - controls is a plot is generated;
    write_roc - controls whether a text file is generated;
    levelbased - controls whether the database is re-read on each iteration of the
                 processing; if False then profiles are not considered again
                 once an accepted test has flagged them; if True, the levels that
                 are flagged are removed so other problems in the profile can be
                 used to determine the best quality control checks to use.
    '''

    # Check that the options make sense.
    if levelbased:
        assert mark_training == False, 'Cannot use mark_training with levelbased'

    # Define the order of tests.
    ordering = ['Location', 'Range', 'Climatology', 'Increasing depth', 'Constant values',
'Spike or step', 'Gradient', 'Density']

    # Read QC test specifications.
    groupdefinition = read_qc_groups()

    # Create results list.
    qclist = []

    keepgoing = True
    iit       = 0
    while keepgoing:
        if iit < len(ordering):
            grouptofind = ordering[iit]
        else:
            grouptofind = 'any'
        if verbose: print('-- Iteration ', iit + 1, ' to find test of type ', grouptofind)
        
        if (iit == 0) or levelbased:
            if verbose: print('---- Running database read')
            # Read data from database into a pandas data frame.
            df = dbutils.db_to_df(table = table,
                                  targetdb = targetdb,
                                  filter_on_wire_break_test = False,
                                  filter_on_tests = groupdefinition,
                                  n_to_extract = n_profiles_to_analyse,
                                  pad=2, 
                                  XBTbelow=True)

            # mark chosen profiles as part of the training set 
            if mark_training:
                all_uids = main.dbinteract('SELECT uid from ' + table + ';', targetdb=targetdb)
                for uid in all_uids:
                    uid = uid[0]
                    is_training = int(uid in df['uid'].astype(int).to_numpy())
                    query = "UPDATE " + table + " SET training=" + str(is_training) + " WHERE uid=" + str(uid) + ";"
                    main.dbinteract(query, targetdb=targetdb)

            # Drop nondiscriminating tests i.e. those that flag all or none
            # of the profiles.
            nondiscrim = []
            cols = list(df.columns)
            for c in cols:
                if len(pandas.unique(df[c])) == 1:
                    nondiscrim.append(c)
                    if verbose: print(c + ' is nondiscriminating and will be removed')
            cols = [t for t in cols if t not in nondiscrim]
            df = df[cols]
            testNames = df.columns[2:].values.tolist()
            
            # Convert to numpy structures and save copy if first iteration.
            truth = df['Truth'].to_numpy()
            tests = []
            for i, tn in enumerate(testNames):
                results = df[tn].to_numpy()
                tests.append(results)
            cumulative = truth.copy()
            cumulative[:] = False
            if iit == 0:
                alltruth = df['Truth'].to_numpy()
                alltests = []
                for i, tn in enumerate(testNames):
                    results = df[tn].to_numpy()
                    alltests.append(results)
                allnames = testNames.copy()
                    
            del df # No further need for the data frame.

        # Try to select a QC check to add to the set.
        if verbose: print('---- Selecting the QC check')
        if grouptofind == 'any':
            testnamestosearch = testNames
        else:
            testnamestosearch = groupdefinition['At least one from group'][grouptofind]

        # Find the best choice from all the QC tests in this group.
        bestchoice = ''
        bestcost   = return_cost(costratio, 0.0, 100.0)    
        for tn in testnamestosearch:
            if tn in qclist: continue
            for itest, name in enumerate(testNames):
                if name == tn: 
                    cumulativenew      = np.logical_or(cumulative, tests[itest])
                    tpr, fpr, fnr, tnr = main.calcRates(cumulativenew, truth)
                    newcost            = return_cost(costratio, tpr, fpr)
                    if verbose: print('    ', tpr, fpr, newcost, bestcost, name)
                    if newcost == bestcost:
                        if verbose:
                            print('  ' + bestchoice + ' and ' + name + ' have the same results and the first is kept')
                    elif newcost < bestcost:
                        bestchoice = name
                        bestcost   = newcost
                        besti      = itest
                        besttpr    = tpr

        # If selecting from any test, need to ensure that it is worth keeping.
        if grouptofind == 'any' and bestchoice != '':
            ctpr, cfpr, cfnr, ctnr = main.calcRates(cumulative, truth)
            currentcost            = return_cost(costratio, ctpr, cfpr)
            if (currentcost < bestcost or 
                (besttpr - ctpr) < improve_threshold):
                bestchoice = ''

        # Record the choice that is made.
        if bestchoice == '':
            if verbose: print('WARNING: no suitable tests in group "' + grouptofind + '", skipping')
            if grouptofind == 'any':
                if verbose: print('End of QC test selection')
                keepgoing = False
        else:
            if verbose: print('  ' + bestchoice + ' was selected from group ' + grouptofind)
            cumulative = np.logical_or(cumulative, tests[besti])
            qclist.append(bestchoice)
            groupdefinition['Remove rejected levels'].append(bestchoice)
            
        # Increment iit to move on to the next group.
        iit += 1

    # Create roc.
    cumulative    = alltruth.copy()
    cumulative[:] = False
    r_fprs        = []
    r_tprs        = []
    for tn in qclist:
        found = False
        for itest, name in enumerate(allnames):
            if tn == name:
                cumulative         = np.logical_or(cumulative, alltests[itest])
                tpr, fpr, fnr, tnr = main.calcRates(cumulative, alltruth)      
                r_fprs.append(fpr)
                r_tprs.append(tpr)
                print('ROC point: ', tpr, fpr, tn)
                found = True
        assert found, 'Error in constructing ROC'

    if plot_roc:
        plt.plot(r_fprs, r_tprs, 'k')
        for i in range(len(r_fprs)):
            colour = 'b'
            plt.plot(r_fprs[i], r_tprs[i], colour + 'o')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.xlabel('False positive rate (%)')
        plt.ylabel('True positive rate (%)')
        plt.savefig(plot_roc)
        plt.close()

    if write_roc:
        f = open(write_roc, 'w')
        r = {}
        r['tpr'] = r_tprs
        r['fpr'] = r_fprs
        r['tests'] = qclist
        json.dump(r, f)
        f.close()

if __name__ == '__main__':

    # parse options
    options, remainder = getopt.getopt(sys.argv[1:], 't:d:n:c:o:p:hslm')
    targetdb = 'iquod.db'
    dbtable = 'iquod'
    outfile = False
    plotfile = False
    samplesize = None
    costratio = [5.0, 5.0]
    ordered = False
    levelbased = False
    mark_training = False
    for opt, arg in options:
        if opt == '-d':
            dbtable = arg
        if opt == '-t':
            targetdb = arg
        if opt == '-n':
            samplesize = int(arg)
        if opt == '-c':
            costratio = ast.literal_eval(arg)
        if opt == '-o':
            outfile = arg
        if opt == '-p':
            plotfile = arg
        if opt == '-s':
            ordered = True
        if opt == '-l':
            levelbased = True
        if opt == '-m':
            mark_training = True
        if opt == '-h':
            print('usage:')
            print('-d <db table name to read from>')
            print('-t <name of db file>')
            print('-n <number of profiles to consider>')
            print('-c <cost ratio array>')
            print('-s Find QC tests in a predefined sequence')
            print('-l If -s, remove only QCed out levels not profiles on each step')
            print('-m If -m, profiles used to generate the ROC will be marked')
            print('-o <filename to write json results out to>')
            print('-p <filename to write roc plot out to>')
            print('-h print this help message and quit')
    if samplesize is None:
        print('please provide a sample size to consider with the -n flag')
        print('-h to print usage')

    if ordered:
        find_roc_ordered(table=dbtable, targetdb=targetdb, n_profiles_to_analyse=samplesize, costratio=costratio, plot_roc=plotfile, write_roc=outfile, levelbased=levelbased, mark_training=mark_training)
    else:
        find_roc(table=dbtable, targetdb=targetdb, n_profiles_to_analyse=samplesize, costratio=costratio, plot_roc=plotfile, write_roc=outfile, mark_training=mark_training)
