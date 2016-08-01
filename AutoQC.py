from wodpy import wod
import glob, time
import numpy as np
import sys, os, data.ds
import util.main as main
import pandas, psycopg2
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
  testNames.remove('EN_std_lev_bkg_and_buddy_check')
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
    cur.execute('SELECT * FROM validate WHERE uid = ' + str(uid) )
    row = cur.fetchall()
    fProfile = tempfile.TemporaryFile()
    fProfile.write(row[0][0]) # a file-like object containing only the profile from the queried row
    fProfile.seek(0)
    profile = wod.WodProfile(fProfile)
    fProfile.close()

    # Check that there are temperature data in the profile, otherwise skip.
    if profile.var_index() is None:
      return
    main.catchFlags(profile)
    if np.sum(profile.t().mask == False) == 0:
      return

    # run tests
    results = [row[0][1]]
    for itest, test in enumerate(testNames):
      
      result = run(test, [profile])
      query = "UPDATE validate SET " + test.lower() + " = " + str(result[0][0]) + " WHERE uid = " + str(profile.uid()) + ";"
      cur.execute(query)
      
  # connect to database & fetch list of all uids
  conn = psycopg2.connect("dbname='root' user='root'")
  cur = conn.cursor()
  cur.execute('SELECT uid FROM validate')
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
  print 'python AutoQC myFile 4'
  print 'will result in output written to results-myFile.csv, and will run the calculation parallelized across 4 cores.'
