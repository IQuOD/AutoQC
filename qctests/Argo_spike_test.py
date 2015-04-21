"""
Implements the spike test on page 8 of http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf
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

    assert len(t.data) == len(d.data), 'Number of temperature measurements does not equal number of depth measurements.'

    # initialize qc as a bunch of falses;
    # implies all measurements pass when a spike can't be calculated, such as at edges & gaps in data:
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)
    isData = isTemperature & isDepth

    for i in range(1,len(t.data)-1):
        if isData[i] & isTemperature[i-1] & isTemperature[i+1]:

          isSpike = numpy.abs(t.data[i] - (t.data[i-1] + t.data[i+1])/2) - numpy.abs((t.data[i+1] - t.data[i-1])/2)
          if d.data[i] < 500:
              qc[i] = isSpike > 6.0
          else:
              qc[i] = isSpike > 2.0

    return qc
