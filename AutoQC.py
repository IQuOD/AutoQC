from dataio import wod
import json, glob, time
import numpy as np

# Create a list of data file names from a json array.
def readInput(JSONlist):
    return json.loads(open(JSONlist).read())

filenames = readInput('datafiles.json')

# Read all profiles from the files and store in a list.
def extractProfiles(filenames):
  profiles = []
  for filename in filenames:
      with open(filename) as f:
          profiles.append(wod.WodProfile(f))
          while profiles[-1].is_last_profile_in_file(f) == False:
              profiles.append(wod.WodProfile(f))
  return profiles

profiles = extractProfiles(filenames)

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

for profile in profiles:
    catchFlags(profile)

# return a list of names of tests foundin <dir>:
def importQC(dir):
  testFiles = glob.glob(dir+'/[!_]*.py')
  testNames = [testFile[len(dir)+1:-3] for testFile in testFiles]

  return testNames

testNames = importQC('qctests')
for testName in testNames:
    exec('from qctests import ' + testName)

# Run every test on every profile;
# Summarize how many profiles fail each test.
nFailedQC  = [0] * len(testNames)
nFailedRef = 0
logfile = open('AutoQClog.' + time.strftime("%H%M%S"), 'w')
for profile in profiles:
    # Run each test on this profile:
    qcResults = []
    for test in testNames:
        exec('qcResults.append(' + test + '.test(profile))')

    # Extract the reference result for each level.
    qcRefs    = profile.t_level_qc(originator=True) >= 3





    # Print out a verbose log of the results.
    logfile.write('Profile ID: %i\n' % profile.uid())

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
    for i in range (0,len(qcRefs)):
      formatString = '{0[0]:<20}{0[1]:<20}'
      row = str(profile.z()[i]) + '  ' + str(profile.t()[i]) + '  '
      for j in range (0, len(qcResults)):
        row += str(qcResults[j][i])
        row += '  '
        formatString += '{0['+str(2+j)+']:<20}'
      row += str(qcRefs[i])
      formatString += '{0['+str(2+len(qcResults))+']:<20}'
      logfile.write(formatString.format(row.split('  ')))
      logfile.write('\n')

    summaryRow = '  OVERALL RESULTS:  '
    formatString = '{0[0]:<20}{0[1]:<20}'
    for i in range (0, len(qcResults)):
      summaryRow += str(np.any(qcResults[i]))
      summaryRow += '  '
      formatString += '{0['+str(2+i)+']:<20}'
    summaryRow += str(np.any(qcRefs))
    formatString += '{0['+str(2+len(qcResults))+']:<20}'
    logfile.write(formatString.format(summaryRow.split('  ')))
    logfile.write('\n')

    logfile.write('-----------------------------------------\n')

    # Collate some statistics:
    for i in range (0, len(qcResults)):
      if np.any(qcResults[i]): nFailedQC[i] += 1
    if np.ma.any(qcRefs): nFailedRef += 1

logfile.close()

print('Number of profiles tested was %i' % len(profiles))
for i in range (0, len(nFailedQC)):
  print('Number of profiles that failed ' + testNames[i] + ' was %i' % nFailedQC[i])
print('Number of profiles that should have been failed was %i' % nFailedRef)
