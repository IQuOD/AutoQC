"""
Implements the wire break test of DOI: 10.1175/JTECHO539.1
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get temperature values from the profile.
    t = p.t()
    d = p.z()

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # only meaningful for XBT data
    if p.probe_type() != 2:
        return qc

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)
    isData = isTemperature & isDepth

    # wire breaks at bottom of profile;
    # don't bother continuing if the bottom level doesn't look like a wb
    if isTemperature[-1] and (t.data[-1] < -2.8 or t.data[-1] > 36):
           qc[-1] = True
    else:
        return qc

    i = 2
    while i<len(t):
        # extreme temperatures at end
        if isTemperature[-1*i] and (t.data[-1*i] < -2.8 or t.data[-1*i] > 36):
            qc[-1*i] = True
        # hard gradient between physical data and wire break
        elif isData[-1*i] and isData[-1*(i+1)]:
            grad = abs((t.data[-1*i] - t.data[-1*(i+1)]) / (d.data[-1*i] - d.data[-1*(i+1)]))
            qc[-1*i] = grad > 0.5

        # break out as soon as wire break behavior ends:
        if not qc[-1*i]:
            break

        i+=1

    return qc
