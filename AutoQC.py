from wodpy import wod
import glob, time
import numpy as np
import sys, os, data.ds
import util.main as main
import pandas
try:
    import psycopg2 as db
    dbtype = 'postgres'
    concom = "dbname='root' user='root'"
except:
    import sqlite3 as db
    concom = 'qcresults.sqlite'
    dbtype = 'sqlite'
from multiprocessing import Pool
import tempfile

def run(test, profiles):
  '''
  run <test> on a list of <profiles>, return an array summarizing when exceptions were raised
  '''
  qcResults = []
  verbose = []
  exec('from qctests import ' + test)
  for profile in profiles:
    exec('result = ' + test + '.test(profile)')

    #demand tests returned bools:
    for i in result:
      assert isinstance(i, np.bool_), str(i) + ' in test result list is of type ' + str(type(i))

    qcResults.append(np.any(result))
    verbose.append(result)
  return [qcResults, verbose]

########################################
# main
########################################

if len(sys.argv)>2:
  # Identify and import tests
  testNames = main.importQC('qctests')
  testNames.sort()
  testNames.remove('EN_track_check')
  print('{} quality control checks have been found'.format(len(testNames)))
  testNames = main.checkQCTestRequirements(testNames)
  print('{} quality control checks are able to be run:'.format(len(testNames)))
  for testName in testNames:
    print('  {}'.format(testName))

  # Parallel processing.
  print('\nPlease wait while QC is performed\n')

  def process_row(uid):
    '''run all tests on the ith database row'''
  
    # extract profile
    profile = main.get_profile_from_db(cur, uid)

    # Check that there are temperature data in the profile, otherwise skip.
    if profile.var_index() is None:
      return
    main.catchFlags(profile)
    if np.sum(profile.t().mask == False) == 0:
      return

    # run tests
    for itest, test in enumerate(testNames):
      
      result = run(test, [profile])
      query = "UPDATE " + sys.argv[1] + " SET " + test.lower() + " = " + str(int(result[0][0])) + " WHERE uid = " + str(profile.uid()) + ";"
      cur.execute(query)
      if dbtype == 'sqlite':
          # Seem to need to do this after every update for sqlite database.
          conn.commit()
      
  # connect to database & fetch list of all uids
  conn = db.connect(concom)
  cur = conn.cursor()
  cur.execute('SELECT uid FROM ' + sys.argv[1])
  uids = cur.fetchall()
  
  # launch async processes
  pool = Pool(processes=int(sys.argv[2]))
  for i in range(len(uids)):
    pool.apply_async(process_row, (uids[i][0],))
  pool.close()
  pool.join()
  
  conn.commit()
  
else:
  print 'Please add command line arguments to name your output file and set parallelization:'
  print 'python AutoQC databasetable 4'
  print 'will result in output written to table in the database, and will run the calculation parallelized across 4 cores.'
