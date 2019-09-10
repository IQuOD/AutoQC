"""
Implements the background check on reported levels from the EN quality control
system, http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

from . import EN_spike_and_step_check
import gsw
import numpy as np
import util.obs_utils as outils
from netCDF4 import Dataset
import util.main as main

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Check if the QC of this profile was already done and if not
    # run the QC.
    #query = 'SELECT en_background_check FROM {} WHERE uid = {};'.format(parameters["table"], p.uid())
    #qc_log = main.dbinteract(query)
    #qc_log = main.unpack_row(qc_log[0])

    #if qc_log[0] is not None:
    #    return qc_log[0]

    return run_qc(p, parameters)

def run_qc(p, parameters):
    """
    Performs the QC check.
    """

    # Define an array to hold results.
    qc = np.zeros(p.n_levels(), dtype=bool)

    # Create a record of the processing for use by the background
    # and buddy checks on standard levels.
    origLevels = []
    ptLevels   = []
    bgLevels   = []

    # Find grid cell nearest to the observation.
    ilon, ilat = findGridCell(p, parameters['enbackground']['lon'], parameters['enbackground']['lat'])

    # Extract the relevant auxiliary data.
    imonth = p.month() - 1
    clim = parameters['enbackground']['clim'][:, ilat, ilon, imonth]
    bgev = parameters['enbackground']['bgev'][:, ilat, ilon]
    bgStdLevels   = clim # Save for use in another check.
    bgevStdLevels = bgev # Save the full column for use by another check.
    obev = parameters['enbackground']['obev']
    depths = parameters['enbackground']['depth']

    # Remove missing data points.
    iOK = (clim.mask == False) & (bgev.mask == False)
    if np.count_nonzero(iOK) == 0: 
        record_parameters(p, bgStdLevels, bgevStdLevels, origLevels, ptLevels, bgLevels)
        return qc
    clim = clim[iOK]
    bgev = bgev[iOK]
    obev = obev[iOK]
    depths = depths[iOK]

    # Find which levels have data.
    t = p.t()
    s = p.s()
    z = p.z()
    isTemperature = (t.mask==False)
    isSalinity = (s.mask==False)
    isDepth = (z.mask==False)
    isData = isTemperature & isDepth

    # prep pressures ahead of time
    depth = np.ma.filled(z,30000)
    pressures = gsw.p_from_z(-depth, p.latitude())

    # Use the EN_spike_and_step_check to find suspect values.
    suspect = EN_spike_and_step_check.test(p, parameters, suspect=True)

    # Loop over levels.
    for iLevel in range(p.n_levels()):
        if isData[iLevel] == False: continue

        # Get the climatology and error variance values at this level.
        climLevel = np.interp(z[iLevel], depths, clim, right=99999)
        bgevLevel = np.interp(z[iLevel], depths, bgev, right=99999)
        obevLevel = np.interp(z[iLevel], depths, obev, right=99999)
        if climLevel == 99999:
            continue 
        assert bgevLevel > 0, 'Background error variance <= 0'
        assert obevLevel > 0, 'Observation error variance <= 0'
        
        # If at low latitudes the background error variance is increased. 
        # Also, because we are on reported levels instead of standard levels 
        # the variances are increased. NB multiplication factors are squared
        # because we are working with error variances instead of standard
        # deviations.
        if np.abs(p.latitude()) < 10.0: bgevLevel *= 1.5**2
        bgevLevel *= 2.0**2
        
        # Set up an initial estimate of probability of gross error. 
        pge = estimatePGE(p.probe_type(), suspect[iLevel])

        # Calculate potential temperature.
        if isSalinity[iLevel]:
            sLevel = s[iLevel]
        else:
            sLevel = 35.0
        potm = outils.pottem(t[iLevel], sLevel, pressures[iLevel], pressure=True)

        # Do Bayesian calculation.
        evLevel = obevLevel + bgevLevel
        sdiff   = (potm - climLevel)**2 / evLevel
        pdGood  = np.exp(-0.5 * np.min([sdiff, 160.0])) / np.sqrt(2.0 * np.pi * evLevel)
        pdTotal = 0.1 * pge + pdGood * (1.0 - pge)
        pgebk   = 0.1 * pge / pdTotal
              
        if pgebk >= 0.5: 
            qc[iLevel] = True
        else:
            # Store the results.
            origLevels.append(iLevel)
            ptLevels.append(potm)
            bgLevels.append(climLevel)
    record_parameters(p, bgStdLevels, bgevStdLevels, origLevels, ptLevels, bgLevels)

    return qc

def record_parameters(profile, bgStdLevels, bgevStdLevels, origLevels, ptLevels, bgLevels):
    # pack the parameter arrays into the enbackground table
    # for consumption by the buddy check

    bgstdlevels = main.pack_array(bgStdLevels)
    bgevstdlevels = main.pack_array(bgevStdLevels)
    origlevels = main.pack_array(origLevels)
    ptlevels = main.pack_array(ptLevels)
    bglevels = main.pack_array(bgLevels)
    query = "REPLACE INTO enbackground VALUES(?,?,?,?,?,?);"
    main.dbinteract(query, [profile.uid(), bgstdlevels, bgevstdlevels, origlevels, ptlevels, bglevels])


def findGridCell(p, gridLong, gridLat):
    '''
    Find grid cell nearest to the observation p, 
    where gridLong and gridLat are lists of grid coordinates.
    '''
    for i in range(1, len(gridLong)):
        assert gridLong[i] - gridLong[i-1] == gridLong[1] - gridLong[0], 'longitude grid points must be evenly spaced'
    lon = p.longitude()
    grid = gridLong
    nlon = len(grid)
    ilon = int(np.mod(np.round((lon - grid[0]) / (grid[1] - grid[0])), nlon))
    for i in range(1, len(gridLat)):
        assert gridLat[i] - gridLat[i-1] == gridLat[1] - gridLat[0], 'latitude grid points must be evenly spaced'
    lat = p.latitude()
    lat = main.normalize_latitude(lat)
    grid = gridLat
    nlat = len(grid)
    ilat = int( np.round((lat - grid[0]) / (grid[1] - grid[0])) )
    if ilat == nlat: ilat -= 1 # Checks for edge case where lat is ~90.

    assert ilon >=0 and ilon < nlon, 'Longitude is out of range: {} {}'.format(lon, ilon)
    assert ilat >=0 and ilat < nlat, 'Latitude is out of range: {} {}'.format(lat, ilat)

    return ilon, ilat


def estimatePGE(probe_type, isSuspect):
    '''
    Estimates the probability of gross error for a measurement taken by
    the given probe_type. Information from the EN_spike_and_step_check 
    is used here to increase the initial estimate if the observation is suspect.
    '''
    if probe_type in [1,2,3,13,16]:
        pge = 0.05    
    else: 
        pge = 0.01
    if isSuspect:
        pge = 0.5 + 0.5 * pge

    return pge

def readENBackgroundCheckAux():
    '''
    Reads auxiliary information needed by the EN background check.
    '''

    filename = 'data/EN_bgcheck_info.nc'
    nc = Dataset(filename)
    data = {}
    data['lon']   = nc.variables['longitude'][:]
    data['lat']   = nc.variables['latitude'][:]
    data['depth'] = nc.variables['depth'][:]
    data['month'] = nc.variables['month'][:]
    data['clim']  = nc.variables['potm_climatology'][:]
    data['bgev']  = nc.variables['bg_err_var'][:]
    data['obev']  = nc.variables['ob_err_var'][:]
    
    return data

def loadParameters(parameterStore):

    main.dbinteract("DROP TABLE IF EXISTS enbackground")
    main.dbinteract("CREATE TABLE IF NOT EXISTS enbackground (uid INTEGER PRIMARY KEY, bgstdlevels BLOB, bgevstdlevels BLOB, origlevels BLOB, ptlevels BLOB, bglevels BLOB)")
    parameterStore['enbackground'] = readENBackgroundCheckAux()




