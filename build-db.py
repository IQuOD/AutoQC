# usage: python build-db.py <wod ascii file name> <table name to append to>

from wodpy import wod
import sys, psycopg2
import util.main as main

if len(sys.argv) == 3:

    # connect to database and create a cursor by which to interact with it.
    try:
        conn = psycopg2.connect("dbname='root' user='root'")
    except:
        print "I am unable to connect to the database"

    cur = conn.cursor()

    # Identify tests
    testNames = main.importQC('qctests')
    testNames.sort()

    # set up our table
    query = "CREATE TABLE IF NOT EXISTS " + sys.argv[2] + """(
                raw text,
                truth boolean,
                uid integer,
                year integer,
                month integer,
                day integer,
                time real,
                lat real, 
                long real, 
                cruise integer,
                """
    for i in range(len(testNames)):
        query += testNames[i].lower() + ' boolean'
        if i<len(testNames)-1:
            query += ','
        else:
            query += ');'

    cur.execute(query)

    # populate table from wod-ascii data
    fid = open(sys.argv[1])
    for xx in range(10):
        # extract profile as wodpy object and raw text
        start = fid.tell()
        profile = wod.WodProfile(fid)
        end = fid.tell()
        fid.seek(start)
        raw = fid.read(end-start)
        fid.seek(end)

        # set up dictionary for populating query string
        wodDict = profile.npdict()
        wodDict['raw'] = "'" + raw + "'"
        # Below avoids failures if all profile data are missing.
        # We have no use for this profile in that case so skip it.
        donotuse = False
        try:
            wodDict['truth'] = sum(profile.t_level_qc(originator=True) >= 3) >= 1
        except:
            donotuse = True
        # Cannot process profiles collected before 1900 at present as datetime strftime
        # function used by CoTeDe gives an error.
        if profile.year() < 1900:
            donotuse = True
        if donotuse:
            if profile.is_last_profile_in_file(fid) == True:
                break
            continue

        query = "INSERT INTO " + sys.argv[2] + " (raw, truth, uid, year, month, day, time, lat, long, cruise) "  + """ VALUES(
                    {p[raw]},
                    {p[truth]},
                    {p[uid]},
                    {p[year]},
                    {p[month]},
                    {p[day]},
                    {p[time]},
                    {p[latitude]}, 
                    {p[longitude]}, 
                    {p[cruise]}
                   )""".format(p=wodDict)
        query = query.replace('--', 'NULL')
        query = query.replace('None', 'NULL')
        cur.execute(query)
        if profile.is_last_profile_in_file(fid) == True:
            break

    conn.commit()

else:

    print 'Usage: python build-db.py inputdatafile databasetable' 
