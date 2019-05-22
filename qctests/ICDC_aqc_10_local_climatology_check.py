'''
Python version of climatology check. 
'''

from netCDF4 import Dataset
import numpy as np
import os

# Define global default temperature range.
parmaxover = 33.0
parminover = -2.0

def test(p, parameters):
    '''Return quality control decisions'''

    # Define default QC.
    qc = np.zeros(p.n_levels(), dtype=bool)
    
    # Find grid indices.
    gridshape = parameters['icdc10']['tmin_annual'].shape

    j = int(np.rint((90.0 - p.latitude()) / 0.5))
    if j < 0 or j >= gridshape[1]: return qc
 
    lon = p.longitude()
    if lon >= 180.0 and lon < 360.0: lon -= 360.0
    i = int(np.rint((lon + 180.0) / 0.5))
    if i < 0 or i >= gridshape[2]: return qc

    # Loop through levels.
    t             = p.t()
    z             = p.z()
    isTemperature = (t.mask == False)
    isPressure    = (z.mask == False)
    isData        = isTemperature & isPressure
    fillv         = parameters['icdc10']['fill_value']
    for k in range(p.n_levels()):
        # Require a valid temperature and depth.
        if isData[k] is False: continue

        # Find the grid level that corresponds to the observation depth.
        climdep = -1
        for l in range(len(parameters['icdc10']['depths_annual']) - 1):
            if (z[k] >= parameters['icdc10']['depths_annual'][l] and 
                z[k] < parameters['icdc10']['depths_annual'][l + 1]):
                climdep = l
        if climdep == -1:
            continue

        # If using deeper than the 38th level, use the annual climatological 
        # ranges, otherwise use monthly values.
        if climdep < 37:
            tmin1 = parameters['icdc10']['tmin_monthly'][p.month() - 1, climdep, j, i]
            tmin2 = parameters['icdc10']['tmin_monthly'][p.month() - 1, climdep + 1, j, i]
            tmax1 = parameters['icdc10']['tmax_monthly'][p.month() - 1, climdep, j, i]
            tmax2 = parameters['icdc10']['tmax_monthly'][p.month() - 1, climdep + 1, j, i] 
            if tmin1 == fillv or tmin2 == fillv or tmax1 == fillv or tmax2 == fillv:
                # Need to switch to annual values.
                useannual = True
            else:
                useannual = False
        if climdep >= 37 or useannual:
            tmin1 = parameters['icdc10']['tmin_annual'][climdep, j, i]
            tmin2 = parameters['icdc10']['tmin_annual'][climdep + 1, j, i]
            tmax1 = parameters['icdc10']['tmax_annual'][climdep, j, i]
            tmax2 = parameters['icdc10']['tmax_annual'][climdep + 1, j, i]

        # Switch to global values if got fill values.
        if tmin1 == fillv or tmin2 == fillv or tmax1 == fillv or tmax2 == fillv:
            tmin1 = parminover
            tmin2 = parminover
            tmax1 = parmaxover
            tmax2 = parmaxover

        # Get the temperature range.
        tminfinal = min(tmin1, tmin2)
        tmaxfinal = max(tmax1, tmax2)

        # Flag the data point if outside the range.
        if t[k] < tminfinal or t[k] > tmaxfinal: qc[k] = True

    return qc

def calcParameters(datfile, ncfile, parameterStore):
    # Create storage for the data and initialise to fill values. 
    fillv = -999
    nlat = 340
    nlon = 721
    ndmn = 38
    ndan = 65
    tmin_monthly = np.ndarray([12, ndmn, nlat, nlon]) * 0 + fillv
    tmax_monthly = np.ndarray([12, ndmn, nlat, nlon]) * 0 + fillv
    tmin_annual  = np.ndarray([ndan, nlat, nlon]) * 0 + fillv
    tmax_annual  = np.ndarray([ndan, nlat, nlon]) * 0 + fillv
    lats         = np.ndarray([nlat]) * 0 + fillv
    lons         = np.ndarray([nlon]) * 0 + fillv
    depths       = np.ndarray([ndan]) * 0 + fillv

    # Read data file, calculate ranges and fill out the data arrays. The file
    # is read until the end is reached. This is 76862838 lines.
    fid = open(datfile)
    line = 'dummy'
    while(True):
        line       = fid.readline()
        if line == '': break
        vals       = line.split()
        month      = int  (vals[ 0])
        j          = int  (vals[ 1])
        yc         = float(vals[ 2])
        i          = int  (vals[ 3])
        xc         = float(vals[ 4])
        k          = int  (vals[ 5])
        ze         = float(vals[ 6])
        mbz        = int  (vals[ 7])
        rbub       = float(vals[ 8])
        temmed     = float(vals[ 9])
        temamd     = float(vals[10])
        taver      = float(vals[11])
        tsig       = float(vals[12])
        quart1     = float(vals[13])
        quart3     = float(vals[14])
        couplemedt = float(vals[15])
        salmed     = float(vals[16])
        salamd     = float(vals[17])
        saver      = float(vals[18])
        ssig       = float(vals[19])
        quars1     = float(vals[20])
        quars3     = float(vals[21])
        couplemeds = float(vals[22])

        if couplemedt >= 0.0: 
            powle = -4.0 * couplemedt
            powri =  3.0 * couplemedt
        else:
            powle = -3.0 * couplemedt
            powri =  4.0*couplemedt
        
        trange = 1.5 * (quart3 - quart1)
        qmin = quart1 - trange * np.exp(powle)
        qmax = quart3 + trange * np.exp(powri)

        if qmin < parminover: qmin = parminover
        if qmax > parmaxover: qmax = parmaxover
        if temmed <= -2.0: 
            qmin = parminover
            qmax = parmaxover

        if month <= 12:
            tmin_monthly[month - 1, k - 1, j - 1, i - 1] = qmin
            tmax_monthly[month - 1, k - 1, j - 1, i - 1] = qmax
        else:
            tmin_annual[k - 1, j - 1, i - 1] = qmin
            tmax_annual[k - 1, j - 1, i - 1] = qmax

        lats[j - 1] = yc
        lons[i - 1] = xc
        depths[k - 1] = ze

    fid.close()

    # Store parameters in memory.
    datadict = {}
    datadict['tmin_monthly'] = tmin_monthly
    datadict['tmax_monthly'] = tmax_monthly
    datadict['tmin_annual'] = tmin_annual
    datadict['tmax_annual'] = tmax_annual
    datadict['lats'] = lats
    datadict['lons'] = lons
    datadict['depths_monthly'] = depths[0:ndmn]
    datadict['depths_annual'] = depths
    datadict['fill_value'] = fillv
    parameterStore['icdc10'] = datadict

    # Store parameters in a netCDF file.
    nc = Dataset(ncfile, 'w')

    latd = nc.createDimension('lat', nlat)
    lond = nc.createDimension('lon', nlon)
    dmnd = nc.createDimension('depthm', ndmn)
    dand = nc.createDimension('deptha', ndan)
    mond = nc.createDimension('month', 12)

    latv = nc.createVariable('lat', 'f4', ('lat',))
    lonv = nc.createVariable('lon', 'f4', ('lon',))
    dmnv = nc.createVariable('depthm', 'f4', ('depthm',))
    danv = nc.createVariable('deptha', 'f4', ('deptha',))
    monv = nc.createVariable('month', 'i1', ('month',))
    tlmv = nc.createVariable('tmin_monthly', 'f4', ('month', 'depthm', 'lat', 'lon'), fill_value=fillv)
    tumv = nc.createVariable('tmax_monthly', 'f4', ('month', 'depthm', 'lat', 'lon'), fill_value=fillv)
    tlav = nc.createVariable('tmin_annual', 'f4', ('deptha', 'lat', 'lon'), fill_value=fillv)
    tuav = nc.createVariable('tmax_annual', 'f4', ('deptha', 'lat', 'lon'), fill_value=fillv)

    latv[:] = lats
    lonv[:] = lons
    dmnv[:] = depths[0:ndmn]
    danv[:] = depths
    monv[:] = range(1, 13)
    tlmv[:, :, :, :] = tmin_monthly
    tumv[:, :, :, :] = tmax_monthly
    tlav[:, :, :] = tmin_annual
    tuav[:, :, :] = tmax_annual

    nc.close()

def loadParameters(parameterStore):
    datfile = 'data/global_mean_median_quartiles_medcouple_smoothed.dat'
    ncfile  = 'data/global_mean_median_quartiles_medcouple_smoothed.nc'
    if os.path.isfile(ncfile) is False:
        calcParameters(datfile, ncfile, parameterStore)
    else:
        nc = Dataset(ncfile)
        datadict = {}
        datadict['tmin_monthly'] = nc.variables['tmin_monthly'][:, :, :, :].data
        datadict['tmax_monthly'] = nc.variables['tmax_monthly'][:, :, :, :].data
        datadict['tmin_annual'] = nc.variables['tmin_annual'][:, :, :].data
        datadict['tmax_annual'] = nc.variables['tmax_annual'][:, :, :].data
        datadict['lats'] = nc.variables['lat'][:]
        datadict['lons'] = nc.variables['lon'][:]
        datadict['depths_monthly'] = nc.variables['depthm'][:]
        datadict['depths_annual'] = nc.variables['deptha'][:]
        datadict['fill_value'] = nc.variables['tmin_monthly']._FillValue
        parameterStore['icdc10'] = datadict
        nc.close()

