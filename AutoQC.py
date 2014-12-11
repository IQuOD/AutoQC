from dataio import wod
import json, glob, time
import numpy as np

# Create a list of data file names from a json array.
def readInput(JSONlist):
    return json.loads(open(JSONlist).read())

# Read all profiles from the files and store in a list.
def extractProfiles(filenames):
  profiles = []
  for filename in filenames:
      with open(filename) as f:
          profiles.append(wod.WodProfile(f))
          while profiles[-1].is_last_profile_in_file(f) == False:
              profiles.append(wod.WodProfile(f))
  return profiles

# In some IQuOD datasets temperature values of 99.9 are special values to
# signify not to use the data value. These are flagged here so they are not
# sent to the quality control programs for testing.
def catchFlags(profile):
  index = profile.var_index()
  assert index is not None, 'No temperatures in profile %s' % profile.uid()
  for i in range(profile.n_levels()):
      if profile.profile_data[i]['variables'][index]['Missing']:
          continue
      if profile.profile_data[i]['variables'][index]['Value'] == 99.9:
          profile.profile_data[i]['variables'][index]['Missing'] = True

# return a list of names of tests foundin <dir>:
def importQC(dir):
  testFiles = glob.glob(dir+'/[!_]*.py')
  testNames = [testFile[len(dir)+1:-3] for testFile in testFiles]

  return testNames

# run <test> on a list of <profiles>, return an array summarizing when exceptions were raised
def run(test, profiles):
  qcResults = []
  verbose = []
  for profile in profiles:
    exec('result = ' + test + '.test(profile)')
    qcResults.append(np.any(result))
    verbose.append(result)
  return [qcResults, verbose]

# extract the summary reference result for each profile:
def referenceResults(profiles):
  refResult = []
  verbose = []
  for profile in profiles:
    refAssessment = profile.t_level_qc(originator=True) >= 3
    refResult.append(np.ma.any(refAssessment))
    verbose.append(refAssessment)
  return [refResult, verbose]

# verbose[i][j][k] == result of test i on profile j at depth k
# trueVerbose[i][j] == true result for profile i at depth j
# <profiles> == array of profiles per `extractProfiles`
# <testNames> == array of names returned by `importQC`
def generateLogfile(verbose, trueVerbose, profiles, testNames):
  # open a logfile
  logfile = open('AutoQClog.' + time.strftime("%H%M%S"), 'w')

  # log summary for each profile
  for i in range (0, len(profiles)): # i counts profiles
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
      row = str(profiles[i].z()[j]) + '  ' + str(profiles[i].t()[j]) + '  '
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

########################################
# main
########################################

# identify data files and extract profiles into an array:
filenames = readInput('datafiles.json')
profiles = extractProfiles(filenames)

# tidy up profiles
for profile in profiles:
  catchFlags(profile)

#identify and import tests
testNames = importQC('qctests')
for testName in testNames:
  exec('from qctests import ' + testName)

# run each test, and record its summary & verbose performance
testResults = []
verbose = []
for test in testNames:
  result = run(test,profiles)
  testResults.append(result[0])
  verbose.append(result[1])
# testResults[i][j] now contains a flag indicating the exception raised by test i on profile j

# extract the summary of which profiles should have passed / failed
truth = referenceResults(profiles)
trueResult = truth[0]
trueVerbose = truth[1]
# trueResult[i] now contains a flag indicating the exception expected for profile i.

# Summary statistics
print('Number of profiles tested was %i' % len(profiles))
for i in range (0, len(testNames)):
  print('Number of profiles that failed ' + testNames[i] + ' was %i' % np.sum(testResults[i]))
print('Number of profiles that should have been failed was %i' % np.sum(trueResult))

#logfile
generateLogfile(verbose, trueVerbose, profiles, testNames)
