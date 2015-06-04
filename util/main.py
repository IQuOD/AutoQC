## helper functions used in the top level AutoQC.py

import json, os, glob
from dataio import wod

def readInput(JSONlist):
    '''Create a list of data file names from a json array.'''
    datafiles = json.loads(open(JSONlist).read())

    # assert that a list of data files is found, and all those files exist:
    assert type(datafiles) is list, 'Failed to read a list from datafiles.json'
    for i in datafiles:
      assert os.path.isfile(i), 'datafile ' + i + ' is not found.'

    return datafiles

def extractProfiles(filenames):
  '''Read all profiles from the files and store in a list. Only the profile
     descriptions are read, not the profile data, in order to avoid using
     too much memory.
  '''
  profiles = []
  for filename in filenames:
      with open(filename) as f:
          profiles.append(wod.WodProfile(f, load_profile_data=False))
          while profiles[-1].is_last_profile_in_file(f) == False:
              profiles.append(wod.WodProfile(f, load_profile_data=False))

  # assert all elements of profiles are WodProfiles
  for i in profiles:
    assert isinstance(i, wod.WodProfile), i + ' is not a WodProfile'

  return profiles

def importQC(dir):
  '''
  return a list of names of tests found in <dir>:
  '''
  testFiles = glob.glob(dir+'/[!_]*.py')
  testNames = [testFile[len(dir)+1:-3] for testFile in testFiles]

  return testNames