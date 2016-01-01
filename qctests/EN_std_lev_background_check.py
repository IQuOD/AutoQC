""" 
Implements the background check on standard levels and the buddy check
from the EN quality control system, 
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import EN_background_check
import EN_constant_value_check
import EN_increasing_depth_check
import EN_range_check
import EN_spike_and_step_check
import EN_stability_check
import numpy as np

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Define an array to hold results.
    qc = np.zeros(p.n_levels(), dtype=bool)

    # Obtain the obs minus background differences on standard levels.
    result = stdLevelData(p)
    if result is None: return qc

    # Unpack the results.
    levels, origLevels, assocLevels = result

    # Retrieve the background and observation error variances.
    bgev = EN_background_check.bgev
    obev = EN_background_check.auxParam['obev']

    # Loop through the levels and calculate the PGE.
    pgeData      = np.ma.array(np.ndarray(len(levels)))
    pgeData.mask = True
    for iLevel, level in enumerate(levels):
        if levels.mask[iLevel] or bgev.mask[iLevel]: continue
        bgevLevel = bgev[iLevel]
        if np.abs(p.latitude() < 10.0): bgevLevel *= 1.5**2
        obevLevel = obev[iLevel]
        pge = EN_background_check.estimatePGE(p.probe_type(), False)

        evLevel = obevLevel + bgevLevel
        sdiff   = level**2 / evLevel
        pdGood  = np.exp(-0.5 * np.min([sdiff, 160.0])) / np.sqrt(2.0 * np.pi * evLevel)
        pdTotal = 0.1 * pge + pdGood * (1.0 - pge)
        pgeData[iLevel] = 0.1 * pge / pdTotal

    # Assign the QC flags.
    for i, pge in enumerate(pgeData):
        if pgeData.mask[i]: continue
        if pge < 0.5: continue
        for j, assocLevel in enumerate(assocLevels):
            if assocLevel == i:
                origLevel = origLevels[j]        
                qc[origLevel] = True

    return qc

    
def stdLevelData(p):
    """
    Combines data that have passed other QC checks to create a 
    set of observation minus background data on standard levels.
    """

    # Combine other QC results.
    preQC = (EN_background_check.test(p) | 
             EN_constant_value_check.test(p) | 
             EN_increasing_depth_check.test(p) | 
             EN_range_check.test(p) |
             EN_spike_and_step_check.test(p) | 
             EN_stability_check.test(p))

    # Get the data stored by the EN background check.
    # As it was run above we know that the data held by the
    # module corresponds to the correct profile.
    origLevels = np.array(EN_background_check.origLevels)
    diffLevels = (np.array(EN_background_check.ptLevels) -
                      np.array(EN_background_check.bgLevels))
    nLevels    = len(origLevels)
    if nLevels == 0: return None # Nothing more to do.

    # Remove any levels that failed previous QC.
    use = np.ones(nLevels, dtype=bool)
    for i, origLevel in enumerate(origLevels):
        if preQC[origLevel]: use[i] = False
    nLevels = np.count_nonzero(use)
    if nLevels == 0: return None
    origLevels = origLevels[use]
    diffLevels = diffLevels[use]
    
    # Get the set of standard levels.
    stdLevels = EN_background_check.auxParam['depth']

    # Create arrays to hold the standard level data and aggregate.
    nStdLevels = len(stdLevels)
    levels     = np.zeros(nStdLevels)
    nPerLev    = np.zeros(nStdLevels) 
    z          = p.z()
    assocLevs  = []
    for i, origLevel in enumerate(origLevels):
        # Find the closest standard level.
        j          = np.argmin(np.abs(z[origLevel] - stdLevels))
        assocLevs.append(j)
        levels[j]  += diffLevels[i]
        nPerLev[j] += 1

    # Average the standard levels where there are data.
    iGT1 = nPerLev > 1
    levels[iGT1] /= nPerLev[iGT1]
    levels = np.ma.array(levels)
    levels.mask = False
    levels.mask[nPerLev == 0] = True

    return levels, origLevels, assocLevs

