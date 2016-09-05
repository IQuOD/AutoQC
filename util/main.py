## helper functions used in the top level AutoQC.py

import json, os, glob, time, pandas, csv, sys, fnmatch
import numpy as np
from wodpy import wod
from netCDF4 import Dataset
import testingProfile
from numbers import Number
import sys
import tempfile, psycopg2

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

def get_profile_from_db(uid):
  '''
  Given a unique id found in the current database table, return the corresponding WodPy profile object.
  '''
 
  command = 'SELECT * FROM ' + sys.argv[1] + ' WHERE uid = ' + str(uid)
  row = dbinteract(command)
  return text2wod(row[0][0])

def text2wod(raw):
  '''
  given the raw text of a wod ascii profile, return a wodpy object representing the same.
  '''
  
  fProfile = tempfile.TemporaryFile()
  fProfile.write(raw) # a file-like object containing only the profile from the queried row
  fProfile.seek(0)
  profile = wod.WodProfile(fProfile)
  fProfile.close()
 
  return profile

def dictify(rows, keys):
  '''
  given a list of rows from the db, return a list of dicts in the same order
  representing the same information keyed by the key names found in the tuple <keys>
  '''

  dicts = []

  for i in range(len(rows)):
    d = {}
    for j in range(len(keys)):
      d[keys[j]] = rows[i][j]

    dicts.append(d)

  return dicts

def dbinteract(command, tries=0):
  '''
  execute the given postgres command;
  catch errors and retry a maximum number of times.
  '''

  max_retry = 99
  conn = psycopg2.connect("dbname='root' user='root'")
  conn.autocommit = True
  cur = conn.cursor()
  try:
    cur.execute(command)
    try:
      result = cur.fetchall()
    except:
      result = None
    cur.close()
    conn.close()
    return result
  except psycopg2.Error as e:
    print 'failed', command, 'on try number', tries
    conn.rollback()
    cur.close()
    conn.close()
    if tries < max_retries:
      dbinteract(command, tries+1)
    else:
      return -1
