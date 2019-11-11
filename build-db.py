# usage help: python build-db.py -h

from wodpy import wod
import sys, sqlite3, getopt
import util.main as main
import util.dbutils as dbutils
import numpy as np
import qctests.CSIRO_wire_break
import ast

def assessProfile(p, check_originator_flag_type, months_to_use):
    'decide whether this profile is acceptable for QC or not; False = skip this profile'

    # not interested in standard levels
    if int(p.primary_header['Profile type']) == 1:
        return False

    # no temperature data in profile
    if p.var_index() is None:
        return False

    # temperature data is in profile but all masked out
    if np.sum(p.t().mask == False) == 0:
        return False

    # all depths are less than 10 cm and there are at least two levels (ie not just a surface measurement)
    if np.sum(p.z() < 0.1) == len(p.z()) and len(p.z()) > 1:
        return False

    # no valid originator flag type
    if check_originator_flag_type:
        o_flag = p.originator_flag_type()
        if o_flag is not None and int(o_flag) not in range(1,15):
            return False

    # check month
    if p.month() not in months_to_use:
        return False

    temp = p.t()
    tempqc = p.t_level_qc(originator=True)

    for i in range(len(temp)):
        # don't worry about levels with masked temperature
        if temp.mask[i]:
            continue

        # if temperature isn't masked:
        # it had better be a float
        if not isinstance(temp.data[i], np.float):
            return False
        # needs to have a valid QC decision:
        if tempqc.mask[i]:
            return False
        if not isinstance(tempqc.data[i], np.integer):
            return False
        if not tempqc.data[i] > 0:
            return False

    return True

def encodeTruth(p):
    'encode a per-level true qc array, with levels marked with 99 temperature set to qc code 99'

    truth = p.t_level_qc(originator=True)
    for i,temp in enumerate(p.t()):
        if temp > 99 and temp < 100:
            truth[i] = 99
    return truth

def builddb(infile, check_originator_flag_type = True,
            months_to_use = range(1, 13), outfile='iquod.db', dbtable='iquod'):

    conn = sqlite3.connect(outfile, isolation_level=None)
    cur = conn.cursor()

    # Identify tests
    testNames = main.importQC('qctests')
    testNames.sort()

    # set up our table
    query = "CREATE TABLE IF NOT EXISTS " + dbtable + """(
                raw text,
                truth BLOB,
                uid integer PRIMARY KEY,
                year integer,
                month integer,
                day integer,
                time real,
                lat real,
                long real,
                country text,
                cruise integer,
                ocruise text,
                probe integer,
                training integer,
                flagged integer,
                """
    for i in range(len(testNames)):
        query += testNames[i].lower() + ' BLOB'
        if i<len(testNames)-1:
            query += ','
        else:
            query += ');'

    cur.execute(query)

    # populate table from wod-ascii data
    fid = open(infile)
    uids = []
    good = 0
    bad = 0

    while True:
        # extract profile as wodpy object and raw text
        start = fid.tell()
        profile = wod.WodProfile(fid)
        end = fid.tell()
        fid.seek(start)
        raw = fid.read(end-start)
        fid.seek(end)
        # set up dictionary for populating query string
        p = profile.npdict()
        p['raw'] = "'" + raw + "'"

        # check for duplicate profiles in raw data
        if p['uid'] in uids:
            if profile.is_last_profile_in_file(fid) == True:
                break
            else:
                continue
        uids.append(p['uid'])

        # skip pathological profiles
        isgood = assessProfile(profile, check_originator_flag_type, months_to_use)
        if not isgood and profile.is_last_profile_in_file(fid) == True:
            break
        elif not isgood:
            continue

        # encode temperature error codes into truth array
        truth = encodeTruth(profile)
        p['truth'] = main.pack_array(truth)

        # extract country code
        country = profile.primary_header['Country code']

        # originator cruise
        orig_cruise = profile.originator_cruise()

        # keep tabs on how many good and how many bad profiles have been added to db
        # nowire == index of first wire break level
        wireqc = qctests.CSIRO_wire_break.test(profile, {})
        try:
            nowire = list(wireqc).index(True)
        except:
            nowire = len(truth)
        # flag only counts if its before the wire break:
        flagged = dbutils.summarize_truth(truth[0:nowire])
        if flagged:
            bad += 1
        else:
            good += 1

        query = "INSERT INTO " + dbtable + " (raw, truth, uid, year, month, day, time, lat, long, country, cruise, ocruise, probe, flagged) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        values = (p['raw'], p['truth'], p['uid'], p['year'], p['month'], p['day'], p['time'], p['latitude'], p['longitude'], country, p['cruise'], orig_cruise, p['probe_type'], int(flagged))
        main.dbinteract(query, values, targetdb=outfile)
        if profile.is_last_profile_in_file(fid) == True:
            break

    conn.commit()
    print('number of clean profiles written:', good)
    print('number of flagged profiles written:', bad)
    print('total number of profiles written:', good+bad)

# parse options
options, remainder = getopt.getopt(sys.argv[1:], 'o:i:d:fm:h')
inputdata = None
dbtable = 'iquod'
outfile = 'iquod.db'
origflags = True
months = range(1, 13)
for opt, arg in options:
    if opt == '-o':
        outfile = arg
    if opt == '-i':
        inputdata = arg
    if opt == '-d':
        dbtable = arg
    if opt == '-f':
        origflags = False
    if opt == '-m':
        months = ast.literal_eval(arg)
    if opt == '-h':
        print('usage:')
        print('-d <db table name to create and write to>')
        print('-f dont check originator flags')
        print('-h print this help message and quit')
        print('-i <filename of raw WOD ascii data> (mandatory)')
        print('-o <output file name>')
        print('-m <list of months to include>')
if inputdata is None:
    print('Must provide raw ascii input data file with the flag `-i`')

builddb(inputdata, check_originator_flag_type = origflags, months_to_use = months, outfile = outfile, dbtable = dbtable)

