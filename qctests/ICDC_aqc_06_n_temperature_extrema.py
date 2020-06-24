'''
Python version of check_aqc_06_number_of_temperature_extrema.f. 
Details of the original code are:

c/ DATE:       JANUARY 20 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)

c/ TITLE:      check_aqc_06_number_of_temperature_extrema

c/ PURPOSE:
c    find profiles with unrealistically large number of temperature extrema
'''

from . import ICDC_aqc_01_level_order as ICDC
import numpy as np

def test(p, parameters):
    '''Return quality control decisions.
    '''
    
    # Initialise data.
    qc = np.zeros(p.n_levels(), dtype=bool)
    parminover = -2.3
    parmaxover = 33.0
    levminext  = 6
    deltaext   = 0.5
    maxextre   = 4

    # Check that we have the levels we need.
    nlevels, z, t = ICDC.reordered_data(p, parameters)
    if nlevels <= levminext: return qc

    # Exclude data outside allowed range.
    use  = (t > parminover) & (t <= parmaxover)
    nuse = np.count_nonzero(use)
    if nuse < levminext: return qc 
    z = z[use]
    t = t[use]

    # Find and count the extrema.
    ima = 0
    for i in range(1, nuse - 1):
        pcent = t[i]
        pa = np.abs(pcent - t[i - 1])
        pb = np.abs(pcent - t[i + 1])
        pmin = min(pa, pb)
        if pcent > t[i - 1] and pcent > t[i + 1] and pmin > deltaext:
            ima += 1
        if pcent < t[i - 1] and pcent < t[i + 1] and pmin > deltaext:
            ima += 1
    if ima > maxextre: 
        qc[:] = True

    return qc



