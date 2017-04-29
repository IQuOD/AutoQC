""" 
Implements the WOD range check,
pp 46 http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
"""
import numpy, csv

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get data from the profile.
    t = p.t()
    d = p.z()
    latitude = p.latitude()
    longitude = p.longitude()

    temperatures = {}
    # initialize qc as a bunch of falses (pass by default)
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)
    isData = isTemperature & isDepth
    isLat = isinstance(latitude, float)
    isLong = isinstance(longitude, float)

    if not isLat or not isLong:
        return qc

    depths = parameters['WODtempRanges']['depths']
    gLat, gLong = nearestGrid(latitude, longitude)
    cellCode = parameters['cellCodes'][(gLat, gLong)]
    region = parameters['regionCodes'][cellCode]
    minima = parameters['WODtempRanges'][region]['min']
    maxima = parameters['WODtempRanges'][region]['max']
    
    for i in range(1, p.n_levels()):
        if isData[i] == False: continue

        # find depth bin
        iDepth = 0
        while d[i] > depths[iDepth] and iDepth <= len(depths):
            iDepth += 1

        minTemp = minima[iDepth]
        maxTemp = maxima[iDepth]

        if t[i] < minTemp or t[i] > maxTemp:
            qc[i] = True

    return qc


def nearestGrid(lat, lng):
    '''
    find the nearest grid point to lat, lng.
    grid st. lat is on [-89.5, 89.5] in steps of 1
    and long is on [-179.5, 179.5] in steps of 1
    '''

    gLat = (numpy.round(lat - 0.5) + 0.5 + 90) % 180 - 90
    gLong = (numpy.round(lng - 0.5) + 0.5 + 180) % 360 - 180

    return gLat, gLong

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
  data = numpy.loadtxt(file,delimiter=",",skiprows=1)

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


def loadParameters(parameterStore):

    parameterStore['regionCodes'] = readRegionCodes()
    parameterStore['cellCodes'] = readCellCodes()
    parameterStore['WODtempRanges'] = readWOD_temperature_ranges()
