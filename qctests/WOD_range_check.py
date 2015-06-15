""" 
Implements the WOD range check,
pp 46 http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
"""

import util.main as main
import numpy

# read in parameter files at global scope
ds_regionCodes = main.readRegionCodes()
ds_cellCodes = main.readCellCodes()
ds_WODtempRanges = main.readWOD_temperature_ranges()

def test(p, **kwargs):
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

    depths = ds_WODtempRanges['depths']
    gLat, gLong = nearestGrid(latitude, longitude)
    cellCode = ds_cellCodes[(gLat, gLong)]
    region = ds_regionCodes[cellCode]
    minima = ds_WODtempRanges[region]['min']
    maxima = ds_WODtempRanges[region]['max']
    
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
