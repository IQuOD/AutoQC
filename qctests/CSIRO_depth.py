"""
Implements the gradient test of DOI: 10.1175/JTECHO539.1
All questionable features result in a flag, in order to minimize false negatives
"""

import numpy

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get depth values (m) from the profile.
    d = p.z()
    # is this an xbt?
    isXBT = p.probe_type() == 2

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)

    for i in range(0,len(t.data)-1):
        if isDepth[i]:
            # too-shallow temperatures on XBT probes
            # note we simply flag this profile for manual QC, in order to minimize false negatives.
            if isXBT and d.data[i] < 3.6:
                qc[i] = True

    return qc