# usage: python filter-db.py <full table name> <filtered table name> <number of good / bad profiles to pick>

import sys, sqlite3

if len(sys.argv) == 4:

    conn = sqlite3.connect('iquod.db', isolation_level=None)
    cur = conn.cursor()

    query = "DROP TABLE IF EXISTS " + sys.argv[2]
    cur.execute(query)

    n = sys.argv[3]
    query = "CREATE TABLE " + sys.argv[2] + " AS SELECT * FROM " + sys.argv[1] + " WHERE flagged=0 ORDER BY RANDOM() LIMIT " + str(n)
    cur.execute(query)
    query = "INSERT INTO " + sys.argv[2] + " SELECT * FROM " + sys.argv[1] + " WHERE flagged=1 ORDER BY RANDOM() LIMIT " + str(n)
    cur.execute(query)

    query = "CREATE UNIQUE INDEX uid ON " + sys.argv[2] + "(uid);"
    cur.execute(query)

    conn.commit()
else:

    print("usage: python filter-db.py <full table name> <filtered table name> <number of good / bad profiles to pick>")
