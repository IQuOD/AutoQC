"""
Implements CSIRO's surface spike check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # depths
    d = p.z()
    # is this an xbt?
    isXBT = p.probe_type() == 2

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(d.data), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)

    if not isXBT:
        return qc

    # flag any level that is shallower than 4m and is followed by a level shallower than 8m.
    for i in range(p.n_levels()):
        if isDepth[i]:
            if d.data[i] < 4 and i < p.n_levels()-1: #only interested in depths less than 4m and not at the bottom of the profile.
                if d.data[i+1] < 8:
                    qc[i] = True
            else:
                break

    return qc