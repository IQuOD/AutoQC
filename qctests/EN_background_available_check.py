""" 
The background check on reported levels from the EN quality control 
system, http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf, includes
setting the QC flags if the background is not available at a profile level.
This aspect is separated out in this check.
"""

import numpy as np
from qctests.EN_background_check import auxParam
from qctests.EN_background_check import findGridCell

def test(p, *args):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Define an array to hold results.
    qc = np.zeros(p.n_levels(), dtype=bool)
    
    # Find grid cell nearest to the observation.
    ilon, ilat = findGridCell(p, auxParam['lon'], auxParam['lat'])
        
    # Extract the relevant auxiliary data.
    imonth = p.month() - 1
    clim = auxParam['clim'][:, ilat, ilon, imonth]
    depths = auxParam['depth']
    
    # Remove missing data points.
    iOK = (clim.mask == False)
    if np.count_nonzero(iOK) == 0:
        qc[:] = True 
        return qc
    clim = clim[iOK]
    depths = depths[iOK]
    
    # Find which levels have data.
    t = p.t()
    z = p.z()
    isTemperature = (t.mask==False)
    isDepth = (z.mask==False)
    isData = isTemperature & isDepth

    # Loop over levels.
    for iLevel in range(p.n_levels()):
        if isData[iLevel] == False: continue
        
        # Get the climatology and error variance values at this level.
        climLevel = np.interp(z[iLevel], depths, clim, right=99999)
        if climLevel == 99999:
            qc[iLevel] = True # This could reject some good data if the 
                              # climatology is incomplete, but also can act as
                              # a check that the depth of the profile is 
                              # consistent with the depth of the ocean.
    
    return qc

