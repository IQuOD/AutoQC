## helper functions used in the top level AutoQC.py

import json, os, glob, time, pandas, csv
import numpy as np
from wodpy import wod
from netCDF4 import Dataset

def readInput(JSONlist):
    '''Create a list of data file names from a json array.'''
    datafiles = json.loads(open(JSONlist).read())

    # assert that a list of data files is found, and all those files exist:
    assert type(datafiles) is list, 'Failed to read a list from the specified file.'
    for i in datafiles:
      assert os.path.isfile(i), 'datafile ' + i + ' is not found.'

    return datafiles

def extractProfiles(filenames):
  '''
  Read all profiles from the files and store in a list. Only the profile
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

def profileData(pinfo, currentFile, f):
  '''
  takes a profile info stub as returned by extractProfiles and extracts the whole profile
  from file f.
  '''

  if pinfo.file_name != currentFile:
    if currentFile != '': f.close()
    currentFile = pinfo.file_name
    f = open(currentFile)
  if f.tell() != pinfo.file_position: f.seek(pinfo.file_position)
  return wod.WodProfile(f), currentFile, f

def importQC(dir):
  '''
  return a list of names of tests found in <dir>:
  '''
  testFiles = glob.glob(dir+'/[!_]*.py')
  testNames = [testFile[len(dir)+1:-3] for testFile in testFiles]

  return testNames

def catchFlags(profile):
  '''
  In some IQuOD datasets temperature values of 99.9 are special values to
  signify not to use the data value. These are flagged here so they are not
  sent to the quality control programs for testing.
  '''
  index = profile.var_index()
  assert index is not None, 'No temperatures in profile %s' % profile.uid()
  for i in range(profile.n_levels()):
      if profile.profile_data[i]['variables'][index]['Missing']:
          continue
      if profile.profile_data[i]['variables'][index]['Value'] == 99.9:
          profile.profile_data[i]['variables'][index]['Missing'] = True

def referenceResults(profiles):
  '''
  extract the summary reference result for each profile:
  '''
  refResult = []
  verbose = []
  for profile in profiles:
    refAssessment = profile.t_level_qc(originator=True) >= 3

    #demand reference results returned bools, or masked constants for missing values:
    for i in refAssessment:
      assert isinstance(i, np.bool_) or isinstance(i, np.ma.core.MaskedConstant), str(i) + ' in reference result list is of type ' + str(type(i))

    refResult.append(np.ma.any(refAssessment))
    verbose.append(refAssessment)
  return [refResult, verbose]


def generateCSV(truth, results, tests, name):
  '''
  log resuls as a CSV, columns for tests, rows for profiles.
  '''

  d = {}
  for i, testName in enumerate(tests):
    d[testName] = results[i]

  df = pandas.DataFrame(d)
  df.insert(0, 'True Flags', truth)

  df.to_csv('results-' + name + '.csv')

  return df
