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
import util.main as main
import pickle, sqlite3, io

def test(p, parameters):
    '''Return a set of QC decisions. This corresponds to levels with
       negative depths.
    '''
    
    uid, nlevels, origlevels, zr, tr, qc = level_order(p, parameters)

    return qc

def reordered_data(p, parameters):
    '''Return number levels and depth, temperature in depth order.
       Only non-rejected levels are returned.
    '''

    uid, nlevels, origlevels, zr, tr, qc = level_order(p, parameters)

    return nlevels, zr, tr

def revert_order(p, data, parameters):
    '''Return data in the original profile order. Data rejected in
       the level_order function are returned as missing data.
    '''

    uid, nlevels, origlevels, zr, tr, qc = level_order(p, parameters)

    datar      = np.ma.array(np.ndarray(p.n_levels()), 
                             dtype = data.dtype)
    datar.mask = True

    for i, datum in enumerate(data):
        datar[origlevels[i]] = datum

    return datar

def revert_qc_order(p, qc, parameters):
    '''Return QC array. Missing data values are set to False.'''
    
    qcr = revert_order(p, qc, parameters)
    qcr[qcr.mask] = False
    return qcr

def level_order(p, parameters):
    '''Reorders data into depth order and rejects levels with 
       negative depth.
    '''
    
    # check if the relevant info is already in the db
    query = 'SELECT nlevels, origlevels, zr, tr, qc FROM icdclevelorder WHERE uid = ' + str(p.uid())
    precomputed = main.dbinteract(query, targetdb=parameters["db"])
    if len(precomputed) > 0:
        nlevels = precomputed[0][0]
        origlevels = pickle.load(io.BytesIO(precomputed[0][1]))
        zr = pickle.load(io.BytesIO(precomputed[0][2]))
        tr = pickle.load(io.BytesIO(precomputed[0][3]))
        qc = pickle.load(io.BytesIO(precomputed[0][4]))
        return p.uid(), nlevels, origlevels, zr, tr, qc

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

    # register pre-computed arrays in db for reuse    
    origlevels_p = pickle.dumps(origlevels, -1)
    zr_p = pickle.dumps(zr, -1)
    tr_p = pickle.dumps(tr, -1)
    qc_p = pickle.dumps(qc, -1)
    
    query = "REPLACE INTO icdclevelorder VALUES(?,?,?,?,?,?)"
    main.dbinteract(query, [p.uid(), nlevels, sqlite3.Binary(origlevels_p), sqlite3.Binary(zr_p), sqlite3.Binary(tr_p), sqlite3.Binary(qc_p)], targetdb=parameters["db"])

    return p.uid(), nlevels, origlevels, zr, tr, qc

def loadParameters(parameterStore):

    main.dbinteract("CREATE TABLE IF NOT EXISTS icdclevelorder (uid INTEGER PRIMARY KEY, nlevels INTEGER, origlevels BLOB, zr BLOB, tr BLOB, qc BLOB)", targetdb=parameterStore["db"])
