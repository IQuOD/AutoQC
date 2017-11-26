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
                truth BLOB,
                uid integer PRIMARY KEY,
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

        # set up dictionary for populating query string
        p = profile.npdict()
        p['raw'] = "'" + raw + "'"
        # Below avoids failures if all profile data are missing.
        # We have no use for this profile in that case so skip it.
        try:
            p['truth'] = main.pack_array(profile.t_level_qc(originator=True))
        except:
            if profile.is_last_profile_in_file(fid) == True:
                break
            continue

        query = "INSERT INTO " + sys.argv[2] + " (raw, truth, uid, year, month, day, time, lat, long, cruise, probe) values (?,?,?,?,?,?,?,?,?,?,?);"
        values = (p['raw'], p['truth'], p['uid'], p['year'], p['month'], p['day'], p['time'], p['latitude'], p['longitude'], p['cruise'], p['probe_type'])
        main.dbinteract(query, values)

        if profile.is_last_profile_in_file(fid) == True:
            break

    conn.commit()

else:

    print 'Usage: python build-db.py inputdatafile databasetable' 
