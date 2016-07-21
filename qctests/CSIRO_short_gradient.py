"""
Implements CSIRO's short gradient check
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

    # depths
    d = p['z']
    # temperatures
    t = p['t']
    
    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t), dtype=bool)
    
    for i in range(0, p['n_levels']-1 ):
        if main.dataPresent(('t', 'z'), i, p) and main.dataPresent(('t', 'z'), i+1, p):
            deltaD = (d[i+1] - d[i]) 
            deltaT = (t[i+1] - t[i])
            if deltaT == 0:
              continue
            gradshort = deltaD / deltaT 
            if (deltaT > 0.5 and deltaD < 30) or abs(gradshort) < 0.4 or (gradshort > 0 and gradshort < 12.5):
                if abs(deltaT) > 0.4:
                    qc[i] = True

    return qc
