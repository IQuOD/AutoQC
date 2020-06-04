import pandas, sqlite3, json, calendar, time, os, sys
import util.dbutils as dbutils
import util.main as main
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab

figdir = "roc-figs-" + str(calendar.timegm(time.gmtime()))

def generateROC(file='roc.json', maxfpr=0.1):
    '''
    return a function that accepts a dataabse row and evaluates the roc function described in the input, 
    cut off at a max false positive rate of maxfpr percent.
    '''

    with open(file) as json_data:
        d = json.load(json_data)

    # find fpr cutoff:
    cut = 0
    for i in range(len(d['fpr'])):
        if d['fpr'][i] < maxfpr:
            cut = i
        else:
            break

    tests = d['tests'][0:cut+1]

    def e(row):
        result = False
        for t in tests:
            qcs = t.split('&')
            term = True
            for qc in qcs:
                term = term and row[qc]
            result = result or term
        return result

    return e

# going to want per-level truth info for flagging levels in plots
def unpack_truth(results):

    return results.apply(dbutils.unpack_qc)

def plotRow(row):
    p = main.text2wod(row['raw'][1:-1])
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.scatter(p.z(),p.t(), c=row['leveltruth'][0], norm=matplotlib.colors.Normalize(vmin=1, vmax=10), cmap='tab10')
    fig.colorbar(im, ax=ax1)
    plt.xlabel('Depth [m]')
    plt.ylabel('Temperature [C]')
    plt.title(str(p.uid()))
    range = plt.ylim()
    plt.ylim(max(-10, range[0]), min(40, range[1]))
    range = plt.ylim()
    dom = plt.xlim()
    plt.xlim(max(-10, dom[0]), min(10000, dom[1]))
    dom = plt.xlim()
    xmargin = (dom[1] - dom[0])*0.7 + dom[0]
    yspace = (range[1] - range[0])*0.05
    ymargin = (range[1] - range[0])*0.95 + range[0]
    plt.text(xmargin,ymargin - 2*yspace, 'Lat: ' + str(p.latitude()))
    plt.text(xmargin,ymargin - 3*yspace, 'Long: ' + str(p.longitude()))
    plt.text(xmargin,ymargin - 4*yspace, 'Probe: ' + str(p.probe_type()))
    plt.text(xmargin,ymargin - 5*yspace, 'Date: ' + str(p.year()) + '/' + str(p.month()) + '/' + str(p.day())    )
    plt.text(xmargin,ymargin - 6*yspace, 'Originator: ' + str(p.originator_flag_type()))
    if row['Truth'] and row['roc']:
        dir = figdir+'/TP/'
    elif row['Truth'] and not row['roc']:
        dir = figdir+'/FN/'
    elif not row['Truth'] and not row['roc']:
        dir = figdir+'/TN/'
    elif not row['Truth'] and row['roc']:
        dir = figdir+'/FP/'
    pylab.savefig(dir + str(p.uid()) + '.png', bbox_inches='tight')
    plt.close()

def plot_roc(targetdb='iquod.db'):

    # get qc tests
    testNames = main.importQC('qctests')

    # connect to database
    conn = sqlite3.connect(targetdb, isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT truth, raw, ' + ','.join(testNames) + ' FROM ' + sys.argv[1] + ' WHERE training=0;'
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = ['Truth', 'raw'] + testNames

    # unpack truth and qc data
    truth = df[['Truth']].apply(unpack_truth).values.tolist()
    df = df.assign(leveltruth=pandas.Series(truth))
    df[['Truth']] = df[['Truth']].apply(dbutils.parse_truth)
    for t in testNames:
        df[[t]] = df[[t]].apply(dbutils.parse)

    # prepare ROC function
    assessROC = generateROC()
    df['roc'] = df.apply(assessROC, axis=1)

    # set up dirs for figures
    os.makedirs(figdir)
    os.makedirs(figdir + '/FP')
    os.makedirs(figdir + '/FN')
    os.makedirs(figdir + '/TP')
    os.makedirs(figdir + '/TN')

    df.apply(plotRow, axis=1)

if __name__ == '__main__':

    if len(sys.argv) == 2:
        plot_roc()
    else:
        print('Usage - python plot-roc.py tablename')
