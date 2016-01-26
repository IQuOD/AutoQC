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

import ICDC_aqc_01_level_order as ICDC
import numpy as np

def test(p):
    '''Return quality control decisions.
    '''

    # The test is run on re-ordered data.
    nlevels, z, t = ICDC.reordered_data(p)
    qc = np.zeros(nlevels, dtype=bool)
    if nlevels < 3: return qc # Not enough levels to check.

    # Ignore any levels outside of limits.
    parminover = -2.3
    parmaxover = 33.0
    use = (t > parminover) & (t < parmaxover)
    nuse = np.count_nonzero(use)
    if nuse < 3: return qc
    zuse = z[use]
    tuse = t[use]
    origlevels = (np.arange(nlevels))[use]

    # Check for spikes.
    for i in range(1, nuse - 1):
        z13   = zuse[i+1] - zuse[i-1]
        z12   = zuse[i] - zuse[i-1]
        z23   = zuse[i+1] - zuse[i] 
        v1    = tuse[i-1]
        v2    = tuse[i]
        v3    = tuse[i+1]

        a     = 0.5 * (v1 + v3)
        q1    = np.abs(v2 - a)
        q2    = np.abs(0.5 * (v3 - v1))

        spike = q1 - q2

        if z[i] > 2000.0:
            spikemax = 2.0
        elif z[i] > 1000.0:
            spikemax = 3.0
        else:
            spikemax = 4.0

        if spike > spikemax:
            qc[origlevels[i]] = True

    return ICDC.revert_qc_order(p, qc)



