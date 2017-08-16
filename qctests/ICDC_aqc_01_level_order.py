'''
Python version of check_aqc_01_level_order.f with input/output
adjusted to work with the AutoQC testing suite. Details of the 
original code are:

c/ DATE:       JANUARY 14 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)

c/ TITLE:      check_aqc_01_levels_order 

c/ PURPOSE:
c    to check  the original level order; 
c    if necessary to bring the original levels to increasing order
'''

import numpy as np

# Global variables to hold data to avoid having to recalculate order
# repeatedly for the same profile.
uid        = None
nlevels    = 0
origlevels = None
zr         = None
tr         = None
qc         = None

def test(p, parameters):
    '''Return a set of QC decisions. This corresponds to levels with
       negative depths.
    '''
    
    level_order(p)

    return qc

def reordered_data(p):
    '''Return number levels and depth, temperature in depth order.
       Only non-rejected levels are returned.
    '''

    level_order(p)

    return nlevels, zr, tr

def revert_order(p, data):
    '''Return data in the original profile order. Data rejected in
       the level_order function are returned as missing data.
    '''

    level_order(p)

    datar      = np.ma.array(np.ndarray(p.n_levels()), 
                             dtype = data.dtype)
    datar.mask = True

    for i, datum in enumerate(data):
        datar[origlevels[i]] = datum

    return datar

def revert_qc_order(p, qc):
    '''Return QC array. Missing data values are set to False.'''
    
    qcr = revert_order(p, qc)
    qcr[qcr.mask] = False
    return qcr

def level_order(p):
    '''Reorders data into depth order and rejects levels with 
       negative depth.
    '''
    global uid, nlevels, origlevels, zr, tr, qc

    # Check if the module already holds the results for this profile.
    if uid == p.uid() and uid is not None:
        return None

    # Extract data and define the index for each level.
    z          = p.z()
    t          = p.t()
    origlevels = np.arange(p.n_levels())

    # Implement the QC. For this test we only reject negative depths.
    qc = z < 0

    # Remove occurrences of no data at a level and rejected obs.
    use        = (z.mask == False) & (t.mask == False) & (qc == False)
    z          = z[use]
    t          = t[use]
    origlevels = origlevels[use]
    nlevels    = np.count_nonzero(use)

    if nlevels > 1:
        # Sort the data. Using mergesort keeps levels with the same depth 
        # in the same order.
        isort      = np.argsort(z, kind='mergesort')
        zr         = z[isort]
        tr         = t[isort]
        origlevels = origlevels[isort]
    else:
        zr         = z
        tr         = t

    return None


