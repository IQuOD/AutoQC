'''
Python version of check_aqc_08_gradient_check. 
Details of the original code are:

DATE:       JANUARY 27 2016

AUTHOR:     Viktor Gouretski

AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany
'''

import ICDC_aqc_01_level_order as ICDC
import numpy as np

def test(p):
    '''Return quality control decisions.
    '''

    # Global ranges - data outside these bounds are ignored.
    parminover = -2.3
    parmaxover = 33.0

    # The test is run on re-ordered data.
    nlevels, z, t = ICDC.reordered_data(p)
    qc = np.zeros(nlevels, dtype=bool)

    # Calculate gradients and thresholds.
    z0 = z[0:-1]
    z1 = z[1:]
    t0 = t[0:-1]
    t1 = t[1:]
    
    gradients = (t1 - t0) / (z1 - z0)
    zmean     = 0.5 * (z0 + z1)
    zmean[zmean < 1.0] = 1.0

    gradmin = -150.0 / zmean - 0.010
    gradmin[gradmin < -4.0] = -4.0

    gradmax = 100.0 / zmean + 0.015
    gradmax[gradmax > 1.5] = 1.5
    
    # Find where the gradients and outside the thresholds.
    result = np.where(((gradients < gradmin) | (gradients > gradmax)) &
                       (t0 > parminover) & (t1 > parminover) &
                       (t0 < parmaxover) & (t1 < parmaxover))[0]

    # Both levels that form the gradient have to be rejected.
    if len(result) > 0:
        qc[result] = True
        qc[result + 1] = True

    return ICDC.revert_qc_order(p, qc)



