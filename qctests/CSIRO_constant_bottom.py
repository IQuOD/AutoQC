"""
Implements CSIRO's constant-bottom check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy
import util.main as main

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """
    
    # Get temperature values from the profile.
    t = p['t']
    # depths
    d = p['z']
    # is this an xbt?
    isXBT = p['probe_type'] == 2
    latitude = p['latitude']
    
    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t), dtype=bool)

    # need more than one level
    if len(d) < 2:
        return qc
    
    # constant temperature at bottom of profile, for latitude > -40 and bottom two depths at least 30m apart:
    if main.dataPresent(('t', 'z'), -1, p) and main.dataPresent(('t', 'z'), -2, p) and isXBT:
        if t[-1] == t[-2] and latitude > -40 and d[-1] - d[-2] > 30:
            qc[-1] = True
 
    return qc
