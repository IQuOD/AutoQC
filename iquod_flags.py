import numpy, pandas, sqlite3, math
import util.main as main
import util.dbutils as dbutils

def parse(results):
    'lifted from dbutils without the summary'

    return results.apply(dbutils.unpack_qc)

def db_to_df_simplified(table,
             n_to_extract=numpy.iinfo(numpy.int32).max,
             targetdb='data/demo.db',
             batchsize=1000):

    '''
    simplified version of dbutils db_to_df
    Reads the table from targetdb into a pandas dataframe.
    Set n_to_extract to limit the number of rows extracted to the specified number.
    '''

    # what tests are available
    testNames = main.importQC('qctests')
    testNames.sort()

    # connect to database
    conn = sqlite3.connect(targetdb, isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results and true flags into a dataframe
    query = 'SELECT uid, truth'
    for test in testNames:
        query += ', ' + test.lower()
    query += ' , probe FROM ' + table   
    query += ' WHERE uid IN (SELECT uid FROM ' + table + ' ORDER BY RANDOM() LIMIT ' + str(n_to_extract) + ')' 

    cur.execute(query)
    rawresults = cur.fetchall()
    
    # Loop over the profiles, 1000 profiles at a time.
    sub  = batchsize # Number of profiles to process at a time.
    nsub = math.ceil(len(rawresults)/sub) # Number of batches of 1000 profiles there will be.
    df_final = None
    testNamesSave = testNames.copy()
    for i in range(nsub):
        # Define the start and end points of this batch of profiles and create a dataframe from them.
        istart = i * sub
        iend   = min((i + 1) * sub, len(rawresults))
        df = pandas.DataFrame(rawresults[istart:iend]).astype('bytes')
        df.columns = ['uid', 'Truth'] + testNamesSave + ['probe']
        df = df.astype({'uid': 'int'})
        df = df.astype({'probe': 'int'})
         
        testNames = df.columns[2:-1].values.tolist()
        df[['Truth']] = df[['Truth']].apply(parse)
        df[testNames] = df[testNames].apply(parse)

        # Keep the results.
        if i == 0:
            df_final = df
        else:
            df_final = pandas.concat([df_final, df])

    return df_final.reset_index(drop=True)

def combotests(row, qctests):
    '''
    given a row from the dataframe returned by db_to_df_simplified
    and a list qctests of strings matching df qc column names to be ORed to generate a flag,
    return a list indicating if any of the provided qc tests flagged the corresponding level
    '''

    nLevels = len(row['Truth'])
    levelFlags = [False]*nLevels

    for i in range(nLevels):
        testresults = [row[test][i] for test in qctests]
        levelFlags[i] = any(testresults)

    return levelFlags

def genflag(HTPRresults, Compresults, LFPRresults, isXBT):
    '''
    given per-level lists of results for each of HTPR, Comp and LFPR cases,
    assess the appropriate IQuOD flag per our paper's prescription
    if isXBT, flags should be monotonically increasing with depth, meaning higher flags propagate to all deeper levels
    '''

    flag = [1]*len(HTPRresults)
    minFlag = 1
    for i in range(len(HTPRresults)):
        flag[i] = minFlag
        if HTPRresults[i]:
            flag[i] = max(2, minFlag)
            if isXBT:
                minFlag = max(2, minFlag)
       	if Compresults[i]:
       	    flag[i] = max(3, minFlag)
       	    if isXBT:
       	       	minFlag	= max(3, minFlag)
       	if LFPRresults[i]:
       	    flag[i] = max(4, minFlag)
       	    if isXBT:
       	       	minFlag	= max(4, minFlag)

    return flag

    
df = db_to_df_simplified('iquod')

HTPR = ['Argo_impossible_date_test', 'Argo_impossible_location_test', 'IQUOD_bottom', 'ICDC_aqc_01_level_order', 'CSIRO_wire_break', 'Argo_global_range_check', 'ICDC_aqc_09_local_climatology_check', 'CoTeDe_GTSPP_WOA_normbias', 'EN_std_lev_bkg_and_buddy_check', 'CSIRO_constant_bottom', 'ICDC_aqc_06_n_temperature_extrema', 'CoTeDe_tukey53H', 'AOML_spike', 'CSIRO_long_gradient', 'ICDC_aqc_08_gradient_check', 'CoTeDe_anomaly_detection', 'EN_background_available_check', 'CSIRO_depth', 'IQuOD_gross_range_check', 'EN_range_check', 'ICDC_aqc_10_local_climatology_check', 'AOML_climatology_test', 'EN_constant_value_check', 'AOML_constant', 'Argo_spike_test', 'ICDC_aqc_07_spike_check', 'EN_spike_and_step_suspect', 'AOML_gradient', 'CSIRO_short_gradient']
Comp = ['Argo_impossible_date_test', 'Argo_impossible_location_test', 'EN_background_available_check', 'ICDC_aqc_01_level_order', 'CSIRO_depth', 'IQuOD_gross_range_check', 'WOD_range_check', 'AOML_climatology_test',  'CoTeDe_GTSPP_WOA_normbias', 'EN_increasing_depth_check', 'EN_constant_value_check', 'EN_spike_and_step_check',  'CSIRO_long_gradient', 'ICDC_aqc_08_gradient_check', 'EN_stability_check']
LFPR = ['Argo_impossible_date_test', 'Argo_impossible_location_test', 'loose_location_at_sea', 'ICDC_aqc_01_level_order', 'IQuOD_gross_range_check', 'WOD_range_check', 'ICDC_aqc_02_crude_range', 'EN_background_check', 'EN_std_lev_bkg_and_buddy_check', 'EN_increasing_depth_check', 'ICDC_aqc_05_stuck_value', 'EN_spike_and_step_check', 'CSIRO_long_gradient', 'EN_stability_check']

for i in range(len(df)):
    HTPRflags = combotests(df.iloc[i], HTPR)
    Compflags = combotests(df.iloc[i], Comp)
    LFPRflags = combotests(df.iloc[i], LFPR)
    iquodFlag = genflag(HTPRflags, Compflags, LFPRflags, df['probe'][i]==2)
    print(iquodFlag)
