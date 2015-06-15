## helper functions used in the top level AutoQC.py

import json, os, glob, time
import numpy as np
from dataio import wod
from netCDF4 import Dataset
import csv

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

def readENBackgroundCheckAux(testNames, kwargs):
  '''
  Reads auxiliary information needed by the EN background check.
  '''
  filename = 'data/EN_bgcheck_info.nc'
  if 'EN_background_check' in testNames and os.path.isfile(filename):
    nc = Dataset(filename)
    data = {}
    data['lon']   = nc.variables['longitude'][:]
    data['lat']   = nc.variables['latitude'][:]
    data['depth'] = nc.variables['depth'][:]
    data['month'] = nc.variables['month'][:]
    data['clim']  = nc.variables['potm_climatology'][:]
    data['bgev']  = nc.variables['bg_err_var'][:]
    data['obev']  = nc.variables['ob_err_var'][:]
    kwargs['EN_background_check_aux'] = data
  else:
    kwargs['EN_background_check_aux'] = None


def readRegionCodes(filename='data/regionCodes.csv'):
    '''
    read region codes from filename
    filename is csv with one title row, and entries formatted as:
    name,code
    filename must have all consecutive codes from 1..n in order
    returns a list regions such that
    regions[code] = name
    '''

    regions = [None]
    file = open(filename)

    reader = csv.reader(file)
    header = True
    for row in reader:
      if header:
        header = False
        continue
      regions.append(row[0])


    return regions


def readCellCodes(filename='data/range_area.csv'):
  '''
  reads filename, a csv with one header row,
  and rows like
  lat, long, range_area
  where range_area is the region code corresponding to that lat/long pair.
  reurns a dictionary with (lat, long) tuples for keys and corresponding range_area for values.
  '''

  cellCodes = {}
  file = open(filename)

  reader = csv.reader(file)
  header = True
  for row in reader:
    if header:
      header = False
      continue
    cellCodes[(float(row[0]), float(row[1]))] = int(row[2])

  return cellCodes

def readWOD_temperature_ranges(filename='data/WOD_ranges_Temperature.csv'):
  '''
  reads the ranges from data/WOD_ranges_Temperature.csv into a dictionary with region names for keys,
  each containing an object with keys 'min' and 'max',
  whose values are lists of the corresponding minima and maxima for that region.
  dictionary also contains a key 'depths', whose value is a list of the depths the mins and maxs are reported for.
  '''

  WODtemps = {}
  file = open(filename,'rb')

  #get headers
  reader = csv.reader(file)
  headers = reader.next()
  del reader

  #get real data as array
  data = np.loadtxt(file,delimiter=",",skiprows=1)

  #populate minima and maxima
  for i in range(1,len(headers)):
    if i%2 == 1: #minima
      region = headers[i][0:-4]
      WODtemps[region] = {'min':data[:,i]}
    else: #maxima
      region = headers[i][0:-4]
      WODtemps[region]['max'] = data[:,i]

  # create depth key

  WODtemps['depths'] = data[:,0]

  return WODtemps



