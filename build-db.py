# usage: python build-db.py <wod ascii file name> <table name to append to>

from wodpy import wod
import sys, sqlite3
import util.main as main
import util.dbutils as dbutils
import numpy as np
import qctests.CSIRO_wire_break

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
        if int(p.originator_flag_type()) not in range(1,15):
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
        if not isinstance(temp.data[i], float):
            return False
        # needs to have a valid QC decision:
        if tempqc.mask[i]:
            return False
        if not isinstance(tempqc.data[i], int):
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

def builddb(check_originator_flag_type = True,
            months_to_use = range(1, 13)):

    conn = sqlite3.connect('iquod.db', isolation_level=None)
    cur = conn.cursor()

    # Identify tests
    testNames = main.importQC('qctests')
    testNames.sort()

    # set up our table
    query = "CREATE TABLE IF NOT EXISTS " + sys.argv[2] + """(
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
    fid = open(sys.argv[1])
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

        query = "INSERT INTO " + sys.argv[2] + " (raw, truth, uid, year, month, day, time, lat, long, country, cruise, ocruise, probe, flagged) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        values = (p['raw'], p['truth'], p['uid'], p['year'], p['month'], p['day'], p['time'], p['latitude'], p['longitude'], country, p['cruise'], orig_cruise, p['probe_type'], int(flagged))
        main.dbinteract(query, values)
        if profile.is_last_profile_in_file(fid) == True:
            break

    conn.commit()
    print 'number of clean profiles written:', good
    print 'number of flagged profiles written:', bad
    print 'total number of profiles written:', good+bad

if len(sys.argv) == 3:

    builddb()
    
elif len(sys.argv) == 5:

    months = sys.argv[4].split(',')
    months = [int(x) for x in months]
    builddb(bool(sys.argv[3]), months)  

else:

    print 'Usage: python build-db.py <inputdatafile> <databasetable> <demand originator flags> <list of months to include>' 



