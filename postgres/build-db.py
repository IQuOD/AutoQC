import psycopg2
from wodpy import wod
import sys

# connect to database and create a cursor by which to interact with it.
try:
    conn = psycopg2.connect("dbname='root' user='root'")
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

# set up our table
query = """CREATE TABLE IF NOT EXISTS profiles(
            lat real, 
            long real, 
            uid integer,
            cruise integer,
            year integer,
            month integer,
            day integer,
            time real,
            probetype integer,
            depth real[], 
            temperature real[],
            salinity real[] 
           );"""
cur.execute(query)

# populate table from wod-ascii data
fid = open(sys.argv[1])
while True:
    profile = wod.WodProfile(fid)
    wodDict = profile.npdict()
    wodDict['z'] = "'{" + ",".join(map(str, wodDict['z'])) + "}'"
    wodDict['t'] = "'{" + ",".join(map(str, wodDict['t'])) + "}'"
    wodDict['s'] = "'{" + ",".join(map(str, wodDict['s'])) + "}'"
    
    query = """INSERT INTO profiles VALUES(
                {p[latitude]}, 
                {p[longitude]}, 
                {p[uid]}, 
                {p[cruise]},
                {p[year]},
                {p[month]},
                {p[day]},
                {p[time]},
                {p[probe_type]},
                {p[z]}, 
                {p[t]},
                {p[s]}
               )""".format(p=wodDict)
    query = query.replace('--', 'NULL')
    query = query.replace('None', 'NULL')
    cur.execute(query)
    if profile.is_last_profile_in_file(fid) == True:
        break

conn.commit()
