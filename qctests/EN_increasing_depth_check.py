""" 
Implements the EN increasing depth check. 
"""

import EN_spike_and_step_check
import numpy as np
from collections import Counter
import util.main as main

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """
 
    # check if this test has already been run on this profile:
    query = 'select en_increasing_depth_check from ' + parameters['dbTable'] + ' where uid = ' + str(p.uid()) + ';'
    previousQC = main.dbinteract(query)
    if previousQC[0][0] is not None:
        if previousQC[0][0]:
            qc = np.ones(1, dtype=bool)
        else:
            qc = np.zeros(1, dtype=bool)
        return qc

    # nothing in db, actually run the test: 
    return run_qc(p, parameters)

def run_qc(p, parameters):

    # Get z values from the profile.
    d    = p.z()
    mask = d.mask
    n    = p.n_levels()

    # Initialize qc array.
    qc = np.zeros(n, dtype=bool)

    # if all the depths are the same, flag all levels and finish immediately
    most_common_depth = Counter(d.data).most_common(1)
    if most_common_depth[0][1] == len(d.data):
        qc = np.ones(n, dtype=bool)
        return qc

    # Basic check on each level.
    qc[d < 0]     = True
    qc[d > 11000] = True

    # Now check for inconsistencies in the depth levels.
    comp       = np.ndarray((n, n), dtype=int)
    currentMax = 1
    while currentMax > 0:
        # Comp gets set to 1 if there is not an increase in depth.
        comp[:, :] = 0
        for i in range(n):
            if qc[i] or mask[i]: continue
            for j in range(n):
                if qc[j] or mask[j] or (i == j): continue
                if i < j:
                    if d[i] >= d[j]: comp[i, j] = 1
                else:
                    if d[i] <= d[j]: comp[i, j] = 1
        
        # Check if comp was set to 1 anywhere and which level was
        # most inconsistent with the others.
        currentMax = 0
        currentLev  = -1
        for i in range(n):
            lineSum = np.sum(comp[:, i])
            if lineSum >= currentMax:
                currentMax = lineSum
                currentLev = i

        # Reject immediately if more than one inconsistency or 
        # investigate further if one inconsistency.
        if currentMax > 1:
            qc[currentLev] = True
        elif currentMax == 1:
            # Find out which level it is inconsistent with.
            for i in range(n):
                if comp[i, currentLev] == 1: otherLev = i
            # Check if one was rejected by the spike and step
            # check, otherwise reject both.
            try:
                spikeqc
            except:
                spikeqc = EN_spike_and_step_check.test(p, parameters)
            if spikeqc[currentLev]: qc[currentLev] = True
            if spikeqc[otherLev]:   qc[otherLev]   = True
            if spikeqc[currentLev] == False and spikeqc[otherLev] == False:
                qc[currentLev] = True
                qc[otherLev]   = True

    return qc
