'''
Python version of check_aqc_05_stuck_value.f. Details of the original code are:

c/ DATE:       JANUARY 20 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)

c/ TITLE:      check_aqc_05_stuck_value 

c/ PURPOSE:
c    to check temperature profile for stuck value/unrealistically thick thermostad 
'''

import ICDC_aqc_01_level_order as ICDC
import numpy as np
from util.wod import wod_database

def test(p):
    '''Return quality control decisions.
    '''

    # Default set of QC flags to return.
    qc = np.zeros(p.n_levels(), dtype=bool)

    # Set minimum allowed levels.      
    db = wod_database(p)
    if db == 'OSD':
        minlevs = 7
    elif db == 'CTD':
        minlevs = 50
    elif db == 'PFL':
        minlevs = 20
    elif db == 'APB':
        minlevs = 20
    elif db == 'MBT':
        minlevs = 7
    elif db == 'XBT':
        minlevs = 20
    else:
        return qc # Do not have the information to QC other types.
    
    # Check that we have the levels we need.
    nlevels, z, t = ICDC.reordered_data(p)
    if nlevels <= minlevs: return qc
    
    # Count stuck values.
    n = np.ones(nlevels, dtype=int)
    for i in range(nlevels - minlevs):
        for j in range(i + 1, nlevels):
            diff = np.abs(t[i] - t[j])
            if diff > 0.0001: break
            n[i] += 1

    # Find the largest stuck value range.
    i = np.argmax(n)
    if n[i] < minlevs: return qc
    thick = z[i + n[i] - 1] - z[i]
    if thick >= 200.0: 
        # If setting the QC flags we need to be careful about level order.
        qclo = qc[0:nlevels]
        qclo[i:i+n[i]] = True
        qc = ICDC.revert_qc_order(p, qclo)

    return qc



