"""
Implements CSIRO's bottle check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get temperature values from the profile.
    t = p.t()
    # what probe type is this?
    isBottle = p.probe_type() == 7
    isUnderway = p.probe_type() == 8
    isCTD = p.probe_type() == 4

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)

    # flag any level that is colder than -20 for any of the relevant probe types
    for i in range(p.n_levels()):
        if isTemperature[i]:
            if t.data[i] < -20 and (isBottle or isUnderway or isCTD):
                qc[i] = True

    return qc