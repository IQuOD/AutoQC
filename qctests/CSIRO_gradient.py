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

    # Get temperature values from the profile.
    t = p.t()
    # Get depth values (m) from the profile.
    d = p.z()
    # is this an xbt?
    isXBT = p.probe_type() == 2

    assert len(t.data) == len(d.data), 'Number of temperature measurements does not equal number of depth measurements.'

    # initialize qc as a bunch of falses;
    # implies all measurements pass when a gradient can't be calculated, such as at edges & gaps in data:
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)
    isData = isTemperature & isDepth

    for i in range(0,len(t.data)-1):
        if isData[i] & isData[i+1]:

            gradient = (d.data[i+1] - d.data[i]) / (t.data[i+1] - t.data[i]) 
            
            # gradient flag
            if gradient > -0.4 and gradient < 12.5:
                qc[i] = True

    print qc
    return qc