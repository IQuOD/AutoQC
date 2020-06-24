'''
Python version of check_aqc_07_spike_check.f. 
Details of the original code are:

c/ DATE:       JANUARY 25 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)


c/ TITLE:      check_aqc_07_spike_check

c/ PURPOSE:
c    to check temperature profile for spikes
'''

from . import ICDC_aqc_01_level_order as ICDC
import numpy as np

def test(p, parameters):
    '''Return quality control decisions.
    '''
    
    # The test is run on re-ordered data.
    nlevels, z, t = ICDC.reordered_data(p, parameters)
    qc = np.zeros(nlevels, dtype=bool) # Reordered data may be a subset of available levels.
    defaultqc = np.zeros(p.n_levels(), dtype=bool) # Default QC flags for full set of levels.
    if nlevels < 3: return defaultqc # Not enough levels to check.

    # Ignore any levels outside of limits.
    parminover = -2.3
    parmaxover = 33.0
    use = (t > parminover) & (t < parmaxover)
    nuse = np.count_nonzero(use)
    if nuse < 3: return defaultqc
    zuse = z[use]
    tuse = t[use]
    origlevels = (np.arange(nlevels))[use]

    # Extract sections of the arrays. We are QCing the values
    # in the z2 and v3 arrays.
    z1 = zuse[0:-2]
    z2 = zuse[1:-1]
    z3 = zuse[2:]
    v1 = tuse[0:-2]
    v2 = tuse[1:-1]
    v3 = tuse[2:]
    ol = origlevels[1:-1]

    # Calculate the level of 'spike'.
    z13 = z3 - z1
    z12 = z2 - z1
    z23 = z3 - z2

    a  = 0.5 * (v1 + v3)
    q1 = np.abs(v2 - a)
    q2 = np.abs(0.5 * (v3 - v1))

    spike = q1 - q2

    # Define the threshold at each level.
    spikemax = np.ndarray(nuse - 2)
    spikemax[:]           = 4.0
    spikemax[z2 > 1000.0] = 3.0
    spikemax[z2 > 2000.0] = 2.0

    # Set QC flags.
    qc[ol[spike > spikemax]] = True

    return ICDC.revert_qc_order(p, qc, parameters)



