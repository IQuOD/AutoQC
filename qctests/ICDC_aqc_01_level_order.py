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

def test(p):
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
                             dtype=data.dtype)
    datar.mask = True

    for i, datum in enumerate(data):
        datar[i] = data[origlevels[i]]

    return datar

def level_order(p):
    '''Reorders data into depth order and rejects levels with 
       negative depth.
    '''
    global uid, nlevels, origlevels, zr, tr, qc

    # Check if the module already holds the results for this profile.
    if uid == p.uid() and uid is not None:
        return None

    # Extract data.
    z        = p.z()
    t        = p.t()
    use      = np.ones(p.n_levels(), dtype=bool)
    qc       = np.zeros(p.n_levels(), dtype=bool)

    # Need to cope with occurrences of no data at a level.
    isZ    = (z.mask==False)
    isT    = (t.mask==False)
    isData = isT & isZ
    for i, isDatum in enumerate(isData):
        if not isDatum: use[i] = False

    # Get the indices and data of the levels we are processing.
    levels  = np.arange(p.n_levels())
    levels  = levels[use]
    z       = z[use]
    t       = t[use]
    nlevels = np.count_nonzero(use)

    # Implement the algorithm as provided in the Fortran version.

    zr         = z.copy()
    tr         = t.copy()
    origlevels = levels.copy()
    if nlevels <= 1: 
        return None

    irev = 0
    for k in range(nlevels - 1):
        if z[k+1] < z[k]: irev += 1
    if irev == 0: return None

    numord = order(zr, nlevels)

    for k in range(nlevels):
        ko    = numord[k]
        zr[k] = z[ko]
        tr[k] = t[ko]
        origlevels[k] = levels[ko]
        if zr[k] < 0:
            qc[origlevels[k]] = True

    # Remove negative depth values as do not want to process them
    # again.
    llpos      = zr >= 0.0
    zr         = zr[llpos]
    tr         = tr[llpos]
    origlevels = origlevels[llpos]
    nlevels    = np.count_nonzero(llpos)

    return None

def order(t, n):
    '''Python implementation of program to bring 1-D array of 
       values t to increasing order.'''

    numord = np.ndarray(nlevels)
    used   = np.zeros(nlevels, dtype=bool)
    
    for kk in range(n):
        tmin = np.max(t) + 1 
        for i in range(n):
            if used[i]: continue
            if t[i] < tmin: 
                j    = i
                tmin = t[i]
        numord[kk] = j    
        used[j]    = True

    return numord
