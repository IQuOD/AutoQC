from wodpy import wod
import glob, time
import matplotlib.pyplot as plt
import numpy as np
import sys, os, json
import util.combineTests as combinatorics
import util.benchmarks as benchmarks
import util.main as main

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

def generateLogfile(verbose, trueVerbose, profiles, testNames):
  '''
  verbose[i][j][k] == result of test i on profile j at depth k
  trueVerbose[j][k] == true result for profile j at depth k
  <profiles> == array of profiles per `extractProfiles`
  <testNames> == array of names returned by `importQC`
  '''
  # open a logfile
  logfile = open('AutoQClog.' + time.strftime("%H%M%S"), 'w')

  # log summary for each profile
  for i in range (0, len(profiles)): # i counts profiles
    with open(profiles[i].file_name) as f:
      f.seek(profiles[i].file_position)
      profile = wod.WodProfile(f)
      
    logfile.write('Profile ID: %i\n' % profiles[i].uid())

    # title row
    titleRow = 'Depth (m)  Temp (degC)'
    formatString = '{0[0]:<20}{0[1]:<20}'
    k = 2
    for test in testNames:
        titleRow += '  ' + test
        formatString += '{0['+str(k)+']:<20}'
        k += 1
    titleRow += '  Reference'
    formatString += '{0['+str(k)+']:<20}'
    logfile.write(formatString.format(titleRow.split('  ')))
    logfile.write('\n')

    # row for each depth
    for j in range (0,len(trueVerbose[i])): # j counts depth
      formatString = '{0[0]:<20}{0[1]:<20}'
      row = str(profile.z()[j]) + '  ' + str(profile.t()[j]) + '  '
      for k in range (0, len(verbose)): # k counts tests
        row += str(verbose[k][i][j])
        row += '  '
        formatString += '{0['+str(2+k)+']:<20}'
      row += str(trueVerbose[i][j])
      formatString += '{0['+str(2+len(verbose))+']:<20}'
      logfile.write(formatString.format(row.split('  ')))
      logfile.write('\n')

    summaryRow = '  OVERALL RESULTS:  '
    formatString = '{0[0]:<20}{0[1]:<20}'
    for k in range (0, len(verbose)):
      summaryRow += str(np.any(verbose[k][i]))
      summaryRow += '  '
      formatString += '{0['+str(2+k)+']:<20}'
    summaryRow += str(np.any(trueVerbose[i]))
    formatString += '{0['+str(2+len(verbose))+']:<20}'
    logfile.write(formatString.format(summaryRow.split('  ')))
    logfile.write('\n')

    logfile.write('-----------------------------------------\n')

def parallel_function(f):
    '''
    thanks http://scottsievert.github.io/blog/2014/07/30/simple-python-parallelism/
    '''
    def easy_parallize(f, sequence):
        """ assumes f takes sequence as input, easy w/ Python's scope """
        from multiprocessing import Pool
        pool = Pool(processes=int(sys.argv[2])) # depends on available cores
        result = pool.map(f, sequence) # for i in sequence: result[i] = f(i)
        cleaned = [x for x in result if not x is None] # getting results
        cleaned = np.asarray(cleaned)
        pool.close() # not optimal! but easy
        pool.join()
        return cleaned
    from functools import partial
    return partial(easy_parallize, f)


def processFile(fName):
  profiles = main.extractProfiles([fName])
  print('{} profiles will be read'.format(len(profiles)))

  # identify and import tests
  testNames = main.importQC('qctests')
  testNames.sort()
  print('{} quality control checks will be applied:'.format(len(testNames)))
  for testName in testNames:
    print(' {}'.format(testName))

  # run each test on each profile, and record its summary & verbose performance
  testResults  = []
  testVerbose  = []
  trueResults  = []
  trueVerbose  = []
  firstProfile = True
  delete       = []
  currentFile  = ''
  f = None
  for iprofile, pinfo in enumerate(profiles):
    # Load the profile data.
    p, currentFile, f = main.profileData(pinfo, currentFile, f)
    # Check that there are temperature data in the profile, otherwise skip.
    # A record is kept of the empty profiles.
    if p.var_index() is None:
      delete.append(iprofile)
      continue
    main.catchFlags(p)
    if np.sum(p.t().mask == False) == 0:
      delete.append(iprofile)
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
    # Update user on progress.
    sys.stdout.write('{:5.1f}% complete\r'.format((iprofile+1)*100.0/len(profiles)))
    sys.stdout.flush()
  # testResults[i][j] now contains a flag indicating the exception raised by test i on profile j

  # Remove records of profiles with no temperature data.
  for i in reversed(delete):
    del profiles[i]

  # Summary statistics
  print('Number of profiles tested was %i' % len(profiles))
  for i in range (0, len(testNames)):
    print('Number of profiles that failed ' + testNames[i] + ' was %i' % np.sum(testResults[i]))
  print('Number of profiles that should have been failed was %i' % np.sum(trueResults))

  return trueResults, testResults, testNames

########################################
# main
########################################

# identify data files and extract profile information into an array - this
# information is used by some quality control checks; the profile data are
# read later.
filenames = main.readInput('datafiles.json')

if len(sys.argv)>2:
  processFile.parallel = parallel_function(processFile)
  parallel_result = processFile.parallel(filenames)
  #recombine results
  truth = parallel_result[0][0]
  results = parallel_result[0][1]
  tests = parallel_result[0][2]

  main.generateCSV(truth, results, tests, sys.argv[1])
else:
  print 'Please add command line arguments to name your output file and set parallelization:'
  print 'python AutoQC myFile 4'
  print 'will result in output written to results-myFile.csv, and will run the calculation parallelized across 4 cores.'