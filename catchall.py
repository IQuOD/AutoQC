# algorithm:
# 0. remove from consideration any QC test that fails to produce TPR / FPR >= some tunable threshold
# 1. remove from consideration any bad profile not flagged by any test; put these aside for new qc test design
# 2. accept all individual qc tests with 0% fpr; remove these from consideration, along with all profiles they flag
# 3. form list of ntuple AND combos, add their decisions to consideration
# 4. identify profiles flagged by exactly one combination. Accept that combination, drop all profiles marked by this combination, and drop this combination from further consideration
# 5. drop the remaining combination with the highest false positive rate (note at this step all remaining profiles are flagged by at least two combination, so this will not raise the false negative rate).
# 6. go back to 4; loop until the list of accepted combinations flags all bad profiles not dropped in step 1.

ar =  __import__('analyse-results')
import util.main as main
import util.dbutils as dbutils
import itertools, sys, json, getopt
from operator import itemgetter

def ntuples(names, n=2):
    '''
    given a list of names of tests, form every ntuple up to and including n combinations from the list
    return as a list of tuples.
    '''

    combos = []
    for i in range(2,n+1):
        combos += itertools.combinations(names, i)

    return combos

def amend(combo, df):
    '''
    add a column to df describing the results of combo
    column title will be the combo elements joined with '&'
    '''

    decision = df[combo[0]]
    for test in combo[1:]:
        decision = decision & df[test]

    name = '&'.join(combo)
    return df.assign(xx=decision).rename(index=str, columns={'xx': name})

# parse command line options
options, remainder = getopt.getopt(sys.argv[1:], 't:d:n:o:h')
targetdb = 'iquod.db'
dbtable = 'iquod'
outfile = 'htp.json'
samplesize = None
for opt, arg in options:
    if opt == '-d':
        dbtable = arg
    if opt == '-t':
        targetdb = arg
    if opt == '-n':
        samplesize = int(arg)
    if opt == '-o':
        outfile = arg
    if opt == '-h':
        print('usage:')
        print('-d <db table name to read from>')
        print('-t <name of db file>')
        print('-n <number of profiles to consider>')
        print('-o <filename to write json results out to>')
        print('-h print this help message and quit')
if samplesize is None:
    print('please provide a sample size to consider with the -n flag')
    print('-h to print usage')

# Read QC test specifications if required.
groupdefinition = ar.read_qc_groups()

# Read data from database into a pandas data frame.
df = dbutils.db_to_df(table=dbtable, 
                      targetdb=targetdb,
                      filter_on_wire_break_test = False,
                      filter_on_tests = groupdefinition,
                      n_to_extract = samplesize)
testNames = df.columns[2:].values.tolist()

# declare some downstream constructs
accepted = []
unflagged = []
fprs = []
bad = df.loc[df['Truth']]
bad.reset_index(inplace=True, drop=True)

# mark chosen profiles as part of the training set
all_uids = main.dbinteract('SELECT uid from ' + dbtable + ';', targetdb=targetdb)
for uid in all_uids:
    uid = uid[0]
    is_training = int(uid in df['uid'].astype(int).as_matrix())
    query = "UPDATE " + dbtable + " SET training=" + str(is_training) + " WHERE uid=" + str(uid) + ";"
    main.dbinteract(query, targetdb=targetdb)

# algo. step 0:
# demand individual QC tests have TPR/FPR > some threshold
perf_thresh = 2
drop_tests = []
for test in testNames:
    tpr, fpr, fnr, tnr = main.calcRates(df[test].tolist(), df['Truth'].tolist())
    if fpr > 0 and tpr / fpr < perf_thresh:
        print('dropping', test, '; tpr/fpr = ', tpr/fpr)
        df.drop([test], axis=1)
        bad.drop([test], axis=1)
        drop_tests.append(test)
testNames = [x for x in testNames if x not in drop_tests]

# algo. step 1:
# note profiles that weren't flagged by any test
for i in range(len(bad)):
    if not any(bad.ix[i][testNames]):
        unflagged.append(bad.ix[i]['uid'])
# drop these from consideration
bad = bad[~bad['uid'].isin(unflagged)]

# algo. step 2:
# assess fprs for individual tests
for x in testNames:
    tpr, fpr, fnr, tnr = main.calcRates(df[x].as_matrix(), df['Truth'].as_matrix())
    fprs.append([x, fpr, tpr])

# accept tests that flag bad profiles with no false positives
print('number of bad profiles to consider:', len(bad))
print('these tests accepted for having no false poitives and more than zero true positives:')
for test in fprs:
    if test[1] == 0 and test[2] > 0:
        accepted.append(test[0])
        print(test[0])
        bad = bad[bad[test[0]]==False]
        bad = bad.drop([test[0]], axis=1)
        testNames.remove(test[0])
fprs = [elt for elt in fprs if elt[0] not in accepted]
print('number of bad profiles remaining:', len(bad))

# algo. step 3
# add a column to df for each combo, summarizing its decision for each profile
combos = ntuples(testNames)
combonames = ['&'.join(x) for x in combos]
for combo in combos:
    bad = amend(combo, bad)
    df = amend(combo, df)

# assess tpr, fpr for each test and combo:
for x in combonames:
    tpr, fpr, fnr, tnr = main.calcRates(df[x].as_matrix(), df['Truth'].as_matrix())
    fprs.append([x, fpr, tpr])
fprs.sort(key=lambda tup: tup[1])

# algo. step 4
while len(bad) > 0:
    nosingleflags = True
    for i in range(len(bad)):
        x = bad.ix[i][testNames+combonames]
        if sum(x) == 1:
            winner = x[x].keys()[0]
            accepted.append(winner)		# accept the combo as the only one flagging this bad profile
            ff = [x for x in fprs if x[0] == winner][0][1]
            tf = [x for x in fprs if x[0] == winner][0][2]
            print('accepted', winner, 'tpr=', tf, '; fpr=', ff)
            bad = bad[bad[winner]==False]	# drop all bad profiles flagged by this combo
            bad = bad.drop([winner], axis=1)	# remove the combo from consideration
            testNames = [elt for elt in testNames if elt is not winner]
            combonames = [elt for elt in combonames if elt is not winner]
            fprs = [elt for elt in fprs if elt[0] is not winner]
            nosingleflags=False
            break
    # algo. step 5
    if nosingleflags:
        maxfpr = fprs[-1][0]
        bad = bad.drop([maxfpr], axis=1)
        testNames = [x for x in testNames if x is not maxfpr]
        combonames = [x for x in combonames if x is not maxfpr]
        del fprs[-1]

print('profiles not caught by any test:')
print(unflagged)

f = open(outfile, 'w')
r = {'tests': accepted}
json.dump(r, f)
f.close()
