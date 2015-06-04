""" 
Implements the background check on reported levels from the EN quality control 
system, http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import EN_spike_and_step_check
import numpy as np
import util.obs_utils as outils

def test(p, *args, **kwargs):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Define an array to hold results.
    qc    = np.zeros(p.n_levels(), dtype=bool)

    # Check that we have the auxiliary information we need, otherwise we
    # will just return.
    if kwargs['EN_background_check_aux'] is None: return qc
    
    # If we are here then the auxiliary information is available.
    aux = kwargs['EN_background_check_aux']
    
    # Find grid cell nearest to the observation.
    lon = p.longitude()
    grid = aux['lon']
    nlon = len(grid)
    ilon = np.mod(np.round((lon - grid[0]) / (grid[1] - grid[0])), nlon)
    lat = p.latitude()
    grid = aux['lat']
    nlat = len(grid)
    ilat = np.mod(np.round((lat - grid[0]) / (grid[1] - grid[0])), nlat)
    if ilat == nlat: ilat -= 1 # Checks for edge case where lat is ~90.
    
    assert ilon >=0 and ilon < nlon, 'Longitude is out of range: %f %i' % (lon, ilon)
    assert ilat >=0 and ilat < nlat, 'Latitude is out of range: %f %i' % (lat, ilat)
    
    # Extract the relevant auxiliary data.
    imonth = p.month() - 1
    clim = aux['clim'][:, ilat, ilon, imonth]
    bgev = aux['bgev'][:, ilat, ilon]
    obev = aux['obev']
    depths = aux['depth']
    
    # Remove missing data points.
    iOK = (clim.mask == False) & (bgev.mask == False)
    if np.count_nonzero(iOK) == 0: return qc
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

    # Use the EN_spike_and_step_check to find suspect values.
    suspect = EN_spike_and_step_check.test(p, suspect=True)

    # Loop over levels.
    for iLevel in range(p.n_levels()):
        if isData[iLevel] == False: continue
        
        # Get the climatology and error variance values at this level.
        climLevel = np.interp(z[iLevel], depths, clim, right=99999)
        bgevLevel = np.interp(z[iLevel], depths, bgev, right=99999)
        obevLevel = np.interp(z[iLevel], depths, obev, right=99999)
        if climLevel == 99999:
            qc[iLevel] = True # This could reject some good data if the 
                              # climatology is incomplete, but also can act as
                              # a check that the depth of the profile is 
                              # consistent with the depth of the ocean.
            continue 
        assert bgevLevel > 0, 'Background error variance <= 0'
        assert obevLevel > 0, 'Observation error variance <= 0'
        
        # If at low latitudes the background error variance is increased. 
        # ALso, because we are on reported levels instead of standard levels 
        # the variances are increased. NB multiplication factors are squared
        # because we are working with error variances instead of standard
        # deviations.
        if np.abs(p.latitude() < 10.0): bgevLevel *= 1.5**2
        bgevLevel *= 2.0**2
        
        # Set up an initial estimate of probability of gross error. Information
        # from the EN_spike_and_step_check is used here to increase the initial
        # estimate if the observation is suspect.
        probe_type = p.probe_type()
        if probe_type == 1 or probe_type == 2 or probe_type == 3 or probe_type == 13 or probe_type == 16:
            pge = 0.05    
        else: 
            pge = 0.01
        if suspect[iLevel]:
            pge = 0.5 + 0.5 * pge
    
        # Calculate potential temperature.
        if isSalinity[iLevel]:
            sLevel = s[iLevel]
        else:
            sLevel = 35.0
        potm = outils.pottem(t[iLevel], sLevel, z[iLevel], lat=p.latitude())
    
        # Do Bayesian calculation.
        evLevel = obevLevel + bgevLevel
        sdiff   = (potm - climLevel)**2 / evLevel
        pdGood  = np.exp(-0.5 * np.min([sdiff, 160.0])) / np.sqrt(2.0 * np.pi * evLevel)
        pdTotal = 0.1 * pge + pdGood * (1.0 - pge)
        pgebk   = 0.1 * pge / pdTotal
              
        if pgebk >= 0.5: qc[iLevel] = True
    
    return qc



