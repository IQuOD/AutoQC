"""
Implements the wire break test of DOI: 10.1175/JTECHO539.1
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
    # is this an xbt?
    isXBT = p.probe_type() == 2

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)

    # wire breaks at bottom of profile:
    if isTemperature[-1] and isXBT:
        if t.data[-1] < -2.8 or t.data[-1] > 36:
            qc[-1] = True

    return qc