# usage: python build-db.py <wod ascii file name> <table name to append to>

from wodpy import wod
import sys, sqlite3
import util.main as main

if len(sys.argv) == 3:

    conn = sqlite3.connect('iquod.db', isolation_level=None)
    cur = conn.cursor()

    # Identify tests
    testNames = main.importQC('qctests')
    testNames.sort()

    # set up our table
    query = "DROP TABLE IF EXISTS " + sys.argv[2] + ";"
    cur.execute(query)
    query = "CREATE TABLE " + sys.argv[2] + """(
                raw text,
                truth integer,
                uid integer,
                year integer,
                month integer,
                day integer,
                time real,
                lat real, 
                long real, 
                cruise integer,
                probe integer,
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

    while True:
        # extract profile as wodpy object and raw text
        start = fid.tell()
        profile = wod.WodProfile(fid)
        end = fid.tell()
        fid.seek(start)
        raw = fid.read(end-start)
        fid.seek(end)

        #if profile.uid() != 65781603 and profile.uid() != 563906:
        #    continue

        # set up dictionary for populating query string
        wodDict = profile.npdict()
        wodDict['raw'] = "'" + raw + "'"
        # Below avoids failures if all profile data are missing.
        # We have no use for this profile in that case so skip it.
        try:
            wodDict['truth'] = sum(profile.t_level_qc(originator=True) >= 3) >= 1
        except:
            if profile.is_last_profile_in_file(fid) == True:
                break
            continue

        query = "INSERT INTO " + sys.argv[2] + " (raw, truth, uid, year, month, day, time, lat, long, cruise, probe) "  + """ VALUES(
                    {p[raw]},
                    {p[truth]},
                    {p[uid]},
                    {p[year]},
                    {p[month]},
                    {p[day]},
                    {p[time]},
                    {p[latitude]}, 
                    {p[longitude]}, 
                    {p[cruise]},
                    {p[probe_type]}
                   )""".format(p=wodDict)
        query = query.replace('--', 'NULL')
        query = query.replace('None', 'NULL')
        query = query.replace('True', '1')
        query = query.replace('False', '0')
        cur.execute(query)
        if profile.is_last_profile_in_file(fid) == True:
            break

    conn.commit()

else:

    print 'Usage: python build-db.py inputdatafile databasetable' 
