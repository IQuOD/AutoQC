"""
Implements CSIRO's short gradient check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # depths
    d = p.z()
    # temperatures
    t = p.t()

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)
    isTemperature = (t.mask==False)
    isData = isTemperature & isDepth

    for i in range(0, p.n_levels()-1 ):
        if isData[i] and isData[i+1]:
            deltaD = (d.data[i+1] - d.data[i]) 
            deltaT = (t.data[i+1] - t.data[i])
            if deltaT == 0:
                continue
            gradshort = deltaD / deltaT 
            if (deltaT > 0.5 and deltaD < 30) or abs(gradshort) < 0.4 or (gradshort > 0 and gradshort < 12.5):
                if abs(deltaT) > 0.4:
                    qc[i] = True

    return qc
