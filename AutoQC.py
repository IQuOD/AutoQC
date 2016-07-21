from wodpy import wod
import glob, time
import numpy as np
import sys, os, json, data.ds
import util.main as main
import pandas, psycopg2
from multiprocessing import Pool

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

def processFile(fName):
  # run each test on each profile, and record its summary & verbose performance
  testResults  = []
  testVerbose  = []
  trueResults  = []
  trueVerbose  = []
  profileIDs   = []
  firstProfile = True
  currentFile  = ''
  f = None

  # keep a list of only the profiles in this thread
  data.ds.threadProfiles = main.extractProfiles([fName])
  data.ds.threadFile     = fName

  for iprofile, pinfo in enumerate(data.ds.threadProfiles):
    # Load the profile data.
    p, currentFile, f = main.profileData(pinfo, currentFile, f)
    # Check that there are temperature data in the profile, otherwise skip.
    if p.var_index() is None:
      continue
    main.catchFlags(p)
    if np.sum(p.t().mask == False) == 0:
      continue
    # Run each test.    
    for itest, test in enumerate(testNames):
      result = run(test, [p])
      if firstProfile:
        testResults.append(result[0])
        testVerbose.append(result[1])
      else:
        testResults[itest].append(result[0][0])
        testVerbose[itest].append(result[1][0])
    firstProfile = False
    # Read the reference result.
    truth = main.referenceResults([p])
    trueResults.append(truth[0][0])
    trueVerbose.append(truth[1][0])
    profileIDs.append(p.uid())
  # testResults[i][j] now contains a flag indicating the exception raised by test i on profile j
  
  return trueResults, testResults, profileIDs


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

  def process_row(uid):
    '''run all tests on the ith database row'''

    # extract profile
    cur.execute('SELECT * FROM demo WHERE uid = ' + str(uid) )
    row = cur.fetchall()
    profile = main.row2dict(row[0])

    # data pre-validation
    # ---tbd---
       
    # run tests
    results = [profile['qcflag']]
    for itest, test in enumerate(testNames):
      if test[0:5] != 'CSIRO':  # testing on CSIRO suite for now
        continue
     
      result = run(test, [profile])
      query = "UPDATE demo SET " + test.lower() + " = " + str(result[0][0]) + " WHERE uid = " + str(profile['uid']) + ";"
      cur.execute(query)
      
    print profile['uid']

  # connect to database & fetch list of all uids
  conn = psycopg2.connect("dbname='root' user='root'")
  cur = conn.cursor()
  cur.execute('SELECT uid FROM demo')
  uids = cur.fetchall()

  # launch async processes
  pool = Pool(processes=int(sys.argv[2]))
  for i in range(len(uids)):
    pool.apply_async(process_row, (uids[i][0],))
  pool.close()
  pool.join()
  
  conn.commit()
  

  # -------------------------------------------

  # # Recombine results
  # truth, results, profileIDs = main.combineArrays(parallel_result)

  # # Print summary statistics and write output file.
  # main.printSummary(truth, results, testNames)
  # main.generateCSV(truth, results, testNames, profileIDs, sys.argv[1])
else:
  print 'Please add command line arguments to name your output file and set parallelization:'
  print 'python AutoQC myFile 4'
  print 'will result in output written to results-myFile.csv, and will run the calculation parallelized across 4 cores.'
