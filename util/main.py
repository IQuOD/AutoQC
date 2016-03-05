## helper functions used in the top level AutoQC.py

import json, os, glob, time, pandas, csv, sys, fnmatch
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


def generateCSV(truth, results, tests, primaryKeys, name):
  '''
  log resuls as a CSV, columns for tests, rows for profiles.
  '''

  d = {}
  for i, testName in enumerate(tests):
    d[testName] = results[i]

  df = pandas.DataFrame(d, index=primaryKeys)

  df.insert(0, 'True Flags', truth)

  df.to_csv('results-' + name + '.csv')

  return df # for testing

def parallel_function(f, nfold=2):
    '''
    thanks http://scottsievert.github.io/blog/2014/07/30/simple-python-parallelism/
    '''
    def easy_parallize(f, sequence):
        """ assumes f takes sequence as input, easy w/ Python's scope """
        from multiprocessing import Pool
        pool = Pool(processes=int(nfold)) # depends on available cores
        result = pool.map(f, sequence) # for i in sequence: result[i] = f(i)
        cleaned = [x for x in result if not x is None] # getting results
        cleaned = np.asarray(cleaned)
        pool.close() # not optimal! but easy
        pool.join()
        return cleaned
    from functools import partial
    return partial(easy_parallize, f)

def checkQCTestRequirements(checks):
  '''Reads set of requirements from qctest_requirements.json and
     checks each QC test to see if their requirements are met.
     A list of QC tests that meet requirements are returned.
     Messages are printed to screen if a check does not meet
     its requirements.
  '''

  # Read list of requirements to run the quality control checks.
  # Each requirement is defined in a dictionary. Each must 
  # have an entry called 'applies_to'. This is a list of QC
  # test names or search strings e.g. CoTeDe* that define
  # which QC tests the requirements apply to. Other entries
  # in the dictionary are optional and can include:
  # 'modules' - a list of modules that are required by the test.
  # 'qctests' - a list of other QC tests that are required.
  # 'data' - a list of datafiles (in the data directory) that are needed.
  # The check is repeated until no QC checks failing requirements
  # are found. This is done because a dependency on another QC
  # check may not be found on the first pass.
  with open('qctest_requirements.json') as f:
    reqs = json.load(f)

  # First check for modules and data files.
  changedList = True
  while changedList:
    changedList = False
    okchecks = []
    for check in checks:
      use = True
      for req in reqs:
        applies = False
        for applycheck in req['applies_to']:
          if fnmatch.fnmatch(check, applycheck): applies = True # Needs wildcard functionality.
        if applies:
          if req.has_key('modules'):
            for module in req['modules']:
              try:
                exec('import ' + module)
              except:
                use = False
                print('  ' + check + ' not available without module ' + module)
          if req.has_key('data'):
            for datafile in req['data']:
              if not isinstance(datafile, list):
                datafile = [datafile]
              matchedfile = False
              for datafileitem in datafile:
                if os.path.isfile('data/' + datafileitem): matchedfile=True
              if matchedfile == False:
                use = False
                comment = '  ' + check + ' not available without file'
                for ifileitem, datafileitem in enumerate(datafile):
                    if ifileitem > 0: comment += ' or'
                    comment += ' data/' + datafileitem
                print(comment)
          if req.has_key('qctests'):
            for qctest in req['qctests']:
              if qctest not in checks:
                use = False
                print('  ' + check + ' not available without QC test ' + qctest)

      if use: 
        okchecks.append(check)
      else:
        changedList = True
    checks      = okchecks

  return checks

def calcRates(testResults, trueResults):
  '''Given two boolean numpy arrays or lists, the true and false, positive and negative rates
     are calculated.
  '''
  # Ensure we have numpy arrays.
  testResultsNp = np.array(testResults)
  trueResultsNp = np.array(trueResults)

  # Calculate number of passes, fails.
  nTrueRejects = np.sum(trueResultsNp)
  nTruePasses  = np.sum(trueResultsNp == False)

  nFF = np.sum(np.logical_and(testResultsNp, trueResultsNp))
  nFP = np.sum(np.logical_and(testResultsNp, trueResultsNp == False))
  nPF = np.sum(np.logical_and(testResultsNp == False, trueResultsNp))
  nPP = np.sum(np.logical_and(testResultsNp == False, trueResultsNp == False))

  # Calculate rates.
  tpr = nFF * 100.0 / nTrueRejects
  fpr = nFP * 100.0 / nTruePasses
  fnr = nPF * 100.0 / nTrueRejects
  tnr = nPP * 100.0 / nTruePasses

  return tpr, fpr, fnr, tnr 

def printSummary(truth, results, testNames):

  nProfiles = len(truth)
  print('Number of profiles tested was %i\n' % nProfiles)
  print('%35s %7s %7s %7s %7s %7s' % ('NAME OF TEST', 'FAILS', 'TPR', 'FPR', 'TNR', 'FNR')) 
  overallResults = np.zeros(nProfiles, dtype=bool)
  for i in range (0, len(testNames)):
    overallResults = np.logical_or(overallResults, results[i])
    tpr, fpr, fnr, tnr = calcRates(results[i], truth)
    print('%35s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % (testNames[i], np.sum(results[i]), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))
  tpr, fpr, fnr, tnr = calcRates(overallResults, truth)
  print('%35s %7i %6.1f%1s %6.1f%1s %6.1f%1s %6.1f%1s' % ('RESULT OF OR OF ALL:', np.sum(overallResults), tpr, '%', fpr, '%', tnr, '%', fnr, '%'))


def combineArrays(parallelResults):
  '''
  given the results of processFile() run in parallel on several datasets,
  recombine the results into a single set of lists for output to CSV.
  '''

  truth = parallelResults[0][0]
  results = parallelResults[0][1]
  profileIDs = parallelResults[0][2]
  for pr in parallelResults[1:]:
    truth      += pr[0]
    for itr, tr in enumerate(pr[1]):
      results[itr] += tr
    profileIDs += pr[2]

  return truth, results, profileIDs

def sort_headers(headers):
  '''
  takes a list of headers, and sorts them into a dictionary keyed by cruise number
  containing a list of corresponding headers; 
  header lists are then time sorted.
  '''

  sortedHeaders = {}

  for header in headers:
    if header.cruise() not in sortedHeaders.keys():
      sortedHeaders[header.cruise()] = [header]
    else:
      sortedHeaders[header.cruise()].append(header)

  for key in sortedHeaders.keys():
    sortedHeaders[key] = sorted(sortedHeaders[key], key=lambda header: (header.year(), header.month(), header.day(), header.time()) )

  return sortedHeaders











