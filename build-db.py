# usage: python build-db.py <wod ascii file name> <table name to append to>

try:
    import psycopg2 as db
    dbtype = 'postgres'
    concom = "dbname='root' user='root'"
except:
    import sqlite3 as db
    concom = 'qcresults.sqlite'
    dbtype = 'sqlite'
print('Database type is ' + dbtype)
from wodpy import wod
import sys
import util.main as main

if len(sys.argv) == 3:

    # connect to database and create a cursor by which to interact with it.
    try:
        conn = db.connect(concom)
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
    #while True:
    for i in range(10):
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
        wodDict['truth'] = int(sum(profile.t_level_qc(originator=True) >= 3) >= 1)
    
        query = "INSERT INTO " + sys.argv[2] + " (raw, truth, uid, lat, long, cruise) "  + """ VALUES(
                    {p[raw]},
                    {p[truth]},
                    {p[uid]},
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

    print('Usage: python build-db.py inputdatafile databasetable')
