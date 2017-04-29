from wodpy import wod
import pickle, psycopg2, sys
import numpy as np
import util.main as main
from multiprocessing import Pool


def run(test, profiles, parameters):
  '''
  run <test> on a list of <profiles>, return an array summarizing when exceptions were raised
  '''

  verbose = []
  exec('from qctests import ' + test)
  for profile in profiles:
    exec('result = ' + test + '.test(profile, parameters)')
    verbose.append(result)

  return verbose

def process_row(uid):
  '''run all tests on the indicated database row'''

  # extract profile
  profile = main.get_profile_from_db(uid)

  # Check that there are temperature data in the profile, otherwise skip.
  if profile.var_index() is None:
    return
  main.catchFlags(profile)
  if np.sum(profile.t().mask == False) == 0:
    return

  # run tests
  results = []
  query = "UPDATE " + sys.argv[1] + " SET "
  for itest, test in enumerate(testNames):
    result = run(test, [profile], parameterStore)[0]
    results.append(main.pack_array(result))
    query += test.lower() + "=?,"

  query = query[:-1] + " WHERE uid = " + str(profile.uid()) + ";"
  main.dbinteract(query, results)
########################################
# main
########################################

if len(sys.argv)>2:

  # Identify and import tests
  testNames = main.importQC('qctests')
  testNames.sort()
  print('{} quality control checks have been found'.format(len(testNames)))
  testNames = main.checkQCTestRequirements(testNames)
  print('{} quality control checks are able to be run:'.format(len(testNames)))
  for testName in testNames:
    print('  {}'.format(testName))

  # Parallel processing.
  print('\nPlease wait while QC is performed\n')

  # set up global parmaeter store
  parameterStore = {
    "table": sys.argv[1]
  }
  for test in testNames:
    exec('from qctests import ' + test)
    try:
      exec(test + '.loadParameters(parameterStore)')
    except:
      print 'No parameters to load for', test
      
  # connect to database & fetch list of all uids
  query = 'SELECT uid FROM ' + sys.argv[1] + ' ORDER BY uid;' 
  uids = main.dbinteract(query)
  
  # launch async processes
  pool = Pool(processes=int(sys.argv[2]))
  for i in range(len(uids)):
    pool.apply_async(process_row, (uids[i][0],))
  pool.close()
  pool.join()
    
else:
  print 'Please add command line arguments to name your output file and set parallelization:'
  print 'python AutoQC <database results table> <number of processes>'
  print 'will use <database results table> to log QC results in the database, and run the calculation parallelized over <number of processes>.'
