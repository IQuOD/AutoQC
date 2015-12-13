from wodpy import wod
import glob, time
import numpy as np
import sys, os, json
import util.main as main
import pandas

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


def processFile(fName):
  profiles = main.extractProfiles([fName])
  print('{} profiles will be read'.format(len(profiles)))
  print('')

  # identify and import tests
  testNames = main.importQC('qctests')
  testNames.sort()

  print('{} quality control checks have been found'.format(len(testNames)))
  testNames = main.checkQCTestRequirements(testNames)
  print('{} quality control checks are able to be run:'.format(len(testNames)))
  for testName in testNames:
    print('  {}'.format(testName))
  print('')

  # run each test on each profile, and record its summary & verbose performance
  testResults  = []
  testVerbose  = []
  trueResults  = []
  trueVerbose  = []
  profileIDs   = []
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
    profileIDs.append(p.uid())
    # Update user on progress.
    sys.stdout.write('QC of profiles is {:5.1f}% complete\r'.format((iprofile+1)*100.0/len(profiles)))
    sys.stdout.flush()
  # testResults[i][j] now contains a flag indicating the exception raised by test i on profile j

  # Remove records of profiles with no temperature data.
  for i in reversed(delete):
    del profiles[i]

  # Summary statistics
  print('')
  print('')
  print('Number of profiles tested was %i' % len(profiles))
  print('')
  print('%30s %7s %7s %7s %7s %7s' % ('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR')) 
  overallResults = np.zeros(len(profiles), dtype=bool)
  for i in range (0, len(testNames)):
    overallResults = np.logical_or(overallResults, testResults[i])
    tpr, fpr, fnr, tnr = main.calcRates(testResults[i], trueResults)
    print('%30s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % (testNames[i], np.sum(testResults[i]), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))
  tpr, fpr, fnr, tnr = main.calcRates(overallResults, trueResults)
  print('%30s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % ('RESULT OF OR OF ALL:', np.sum(overallResults), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))

  return trueResults, testResults, testNames, profileIDs


########################################
# main
########################################

# identify data files and extract profile information into an array - this
# information is used by some quality control checks; the profile data are
# read later.
filenames = main.readInput('datafiles.json')

if len(sys.argv)>2:
  processFile.parallel = main.parallel_function(processFile, sys.argv[2])
  parallel_result = processFile.parallel(filenames)
  #recombine results
  truth = parallel_result[0][0]
  results = parallel_result[0][1]
  tests = parallel_result[0][2]
  profileIDs = parallel_result[0][3]
  for pr in parallel_result[1:]:
    truth      += pr[0]
    for itr, tr in enumerate(pr[1]):
      results[itr] += tr
    profileIDs += pr[3]

  main.generateCSV(truth, results, tests, profileIDs, sys.argv[1])
else:
  print 'Please add command line arguments to name your output file and set parallelization:'
  print 'python AutoQC myFile 4'
  print 'will result in output written to results-myFile.csv, and will run the calculation parallelized across 4 cores.'
