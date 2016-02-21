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

import ICDC_aqc_01_level_order as ICDC
from netCDF4 import Dataset
import numpy as np
import os
import time

def test(p):
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

    # Get range.
    ranges = get_climatology_range(nlevels, z, lat, lon, p.month())
    if ranges is None:
        return defaultqc

    # Perform the QC.
    tmin, tmax = ranges
    qc = ((t < tmin) | (t > tmax)) & (tmin != fillValue) & (tmax != fillValue) 

    return ICDC.revert_qc_order(p, qc)

def get_climatology_range(nlevels, z, lat, lon, month):

    # Define arrays for the results.
    tmin = np.ndarray(nlevels)
    tmax = np.ndarray(nlevels)
    tmin[:] = fillValue
    tmax[:] = fillValue

    # Calculate grid indices.
    iy = int(np.floor((90.0 - lat) / 0.5))
    ix = int(np.floor((lon + 180.0) / 0.5))
    if (iy < 0 or iy > 360 or ix < 0 or ix > 720):
        return None
 
    # Find the climatology range.
    for k in range(nlevels):
        # Find the corresponding climatology level.
        arg = np.argwhere((z[k] >= zedqc[:-1]) & (z[k] < zedqc[1:]))
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
            amd = tamdM[ix, iy, kisel, month - 1]
            if amd < 0.0:
                useAnnual = True
            else:
                tmedian = tmedM[ix, iy, kisel, month - 1]
                if tmedian < parminover:
                    useAnnual = True
        if useAnnual:
            amd = tamdA[ix, iy, kisel]
            if amd < 0.0:
                continue
            else:
                tmedian = tmedA[ix, iy, kisel]
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

def read_ascii_and_convert_to_netcdf():
    '''Coverts the ASCII data file to netCDF on first read.
       This is much faster to access.
    '''
    global tmedM, tamdM, tmedA, tamdA, zedqc, fillValue

    # Load the data.
    tmedM             = np.ndarray([721, 361, 16, 12])
    tamdM             = np.ndarray([721, 361, 16, 12])
    tmedA             = np.ndarray([721, 361, 60])
    tamdA             = np.ndarray([721, 361, 60])
    zedqc             = np.ndarray(60)
    # Do not use masked arrays to save on memory use.
    fillValue         = -9.0 # Has to be a negative number.
    tmedM[:, :, :, :] = fillValue
    tamdM[:, :, :, :] = fillValue
    tmedA[:, :, :]    = fillValue
    tamdA[:, :, :]    = fillValue
    with open('data/climatological_t_median_and_amd_for_aqc.dat') as f:
        for line in f:
            vals      = line.split()
            m         = int(vals[0]) - 1
            j         = int(vals[1]) - 1
            i         = int(vals[3]) - 1
            k         = int(vals[5]) - 1
            z         = float(vals[6])
            tmedian   = float(vals[7])
            absmeddev = float(vals[8])

            if m < 12 and k < 16:
                tmedM[i, j, k, m] = tmedian
                tamdM[i, j, k, m] = absmeddev
            elif m == 12:
                tmedA[i, j, k] = tmedian
                tamdA[i, j, k] = absmeddev
            zedqc[k]         = z

    # Create the netCDF version.
    nc = Dataset('data/climatological_t_median_and_amd_for_aqc.nc', 'w')
    idim = nc.createDimension('i', 721)
    jdim = nc.createDimension('j', 361)
    kmdim = nc.createDimension('km', 16)
    kadim = nc.createDimension('ka', 60)
    mdim = nc.createDimension('m', 12)

    sf = 0.0001
    tmedav = nc.createVariable('tmedA', 'i4', ('i', 'j', 'ka'), zlib=True)
    tmedav.add_offset = 0.0
    tmedav.scale_factor = sf
    tmedav[:, :, :] = tmedA

    tamdav = nc.createVariable('tamdA', 'i4', ('i', 'j', 'ka'), zlib=True)
    tamdav.add_offset = 0.0
    tamdav.scale_factor = sf
    tamdav[:, :, :] = tamdA

    tmedmv = nc.createVariable('tmedM', 'i4', ('i', 'j', 'km', 'm'), zlib=True)
    tmedmv.add_offset = 0.0
    tmedmv.scale_factor = sf
    tmedmv[:, :, :, :] = tmedM

    tamdmv = nc.createVariable('tamdM', 'i4', ('i', 'j', 'km', 'm'), zlib=True)
    tamdmv.add_offset = 0.0
    tamdmv.scale_factor = sf
    tamdmv[:, :, :, :] = tamdM

    zedqcv = nc.createVariable('zedqc', 'f4', ('ka',))
    zedqcv[:] = zedqc

    nc.fillValue = fillValue
    nc.history = 'Created ' + time.ctime(time.time()) + ' from climatological_t_median_and_amd_for_aqc.dat provided by Viktor Gouretski, Integrated Climate Data Center, University of Hamburg, Hamburg, Germany, February 2016'
    nc.close()

def read_netcdf():
    '''Read climatological data from netCDF.
    '''
    global tmedM, tamdM, tmedA, tamdA, zedqc, fillValue

    nc = Dataset('data/climatological_t_median_and_amd_for_aqc.nc', 'r')
    tmedA = nc.variables['tmedA'][:, :, :]
    tamdA = nc.variables['tamdA'][:, :, :]
    tmedM = nc.variables['tmedM'][:, :, :, :]
    tamdM = nc.variables['tamdM'][:, :, :, :]
    zedqc = nc.variables['zedqc'][:]
    fillValue = nc.fillValue
    nc.close()

# Global ranges - data outside these bounds are assumed not valid.
parminover = -2.3
parmaxover = 33.0

# Read data.
if os.path.isfile('data/climatological_t_median_and_amd_for_aqc.nc'):
    read_netcdf()
else:
    read_ascii_and_convert_to_netcdf()



