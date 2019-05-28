'''
Python version of check_aqc_09_gradient_check.f. 
Details of the original code are:

c/ DATE:       FEBRUARY 4 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)

c/ TITLE:      local_climatological_range_check - check_aqc_09_climatological_range

c/ PURPOSE:
c    to check wheather temperature value is within the local climatological range

c/ Local temperature median and absolute median deviation are calculated on the basis
c/ of the OSD, CTD, and PFL temperature profiles from the WOD13 (updates as of December 2015)
c/ The median and the amd are calculated on a regular 0.5x0.5 lat/lon grid at 60 depth levels
c/ with level spacing increasing with depth. 
c/ Variable influence area size is used with the target number of 500 profiles within the influence
c/ area. This number is not achieved in the data sparse regions or nn the deep levels.

c     local climatological ranges for the level k are defined as:
c     tminlocal(k)=tmedian(k) - rnumamd*tamd(k)
c     tmaxlocal(k)=tmedian(k) + rnumamd*tamd(k)
'''

from . import ICDC_aqc_01_level_order as ICDC
from netCDF4 import Dataset
import numpy as np
import os
import time

def test(p, parameters):
    '''Return quality control decisions.
    '''
    
    # The test is run on re-ordered data.
    nlevels, z, t = ICDC.reordered_data(p)
    
    # Define default QC.
    defaultqc = np.zeros(p.n_levels(), dtype=bool)
    
    # No check for the Caspian Sea or Great Lakes.
    lat = p.latitude()
    lon = p.longitude()
    if ((lat >= 35.0 and lat <= 45.0 and lon >= 45.0 and lon <= 60.0) or
        (lat >= 40.0 and lat <= 50.0 and lon >= -95.0 and lon <= -75.0)):
        return defaultqc
    
    # parameters
    nc = Dataset('data/climatological_t_median_and_amd_for_aqc.nc', 'r')
    
    # Get range.
    ranges = get_climatology_range(nlevels, z, lat, lon, p.month(), nc)
    if ranges is None:
        return defaultqc
    
    # Perform the QC.
    tmin, tmax = ranges
    qc = ((t < tmin) | (t > tmax)) & (tmin != nc.fillValue) & (tmax != nc.fillValue) 

    return ICDC.revert_qc_order(p, qc)

def get_climatology_range(nlevels, z, lat, lon, month, nc):

    # Define arrays for the results.
    tmin = np.ndarray(nlevels)
    tmax = np.ndarray(nlevels)
    tmin[:] = nc.fillValue
    tmax[:] = nc.fillValue

    # Global ranges - data outside these bounds are assumed not valid.
    parminover = -2.3
    parmaxover = 33.0

    # Calculate grid indices.
    iy = int(np.floor((90.0 - lat) / 0.5))
    ix = int(np.floor((lon + 180.0) / 0.5))
    if (iy < 0 or iy > 360 or ix < 0 or ix > 720):
        return None
 
    # Find the climatology range.
    for k in range(nlevels):
        # Find the corresponding climatology level.
        arg = np.argwhere((z[k] >= nc.variables['zedqc'][:][:-1]) & (z[k] < nc.variables['zedqc'][:][1:]))
        if len(arg) > 0:
            kisel = arg[0]
        else: 
            continue # No level found.
        # Check if using monthly or annual fields.
        if kisel <= 15:
            useAnnual = False
        else:
            useAnnual = True
        if month is None: useAnnual = True 
        # Extract the temperature.       
        if useAnnual == False:
            amd = nc.variables['tamdM'][ix, iy, kisel, month - 1][0]
            if amd < 0.0:
                useAnnual = True
            else:
                tmedian = nc.variables['tmedM'][ix, iy, kisel, month - 1][0]
                if tmedian < parminover:
                    useAnnual = True
        if useAnnual:
            amd = nc.variables['tamdA'][ix, iy, kisel][0]
            if amd < 0.0:
                continue
            else:
                tmedian = nc.variables['tmedA'][ix, iy, kisel][0]
                if tmedian < parminover:
                    continue
        if amd > 0.0 and amd < 0.05: amd = 0.05

        rnumamd = 3.0
        tmaxa   = tmedian + rnumamd * amd
        tmina   = tmedian - rnumamd * amd
        if tmina < parminover: tmina = parminover
        if tmaxa > parmaxover: tmaxa = parmaxover

        tmin[k] = tmina
        tmax[k] = tmaxa

    return tmin, tmax


