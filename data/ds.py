# helper functions for loading data
import csv
import numpy as np

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

# populate on load
regionCodes = readRegionCodes()
cellCodes = readCellCodes()
WODtempRanges = readWOD_temperature_ranges()