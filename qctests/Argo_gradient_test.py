"""
Implements the gradient test on page 8 of http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf
"""

import numpy
from util import obs_utils

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get temperature values from the profile.
    t = p.t()
    # Get depth values (m) from the profile.
    z = obs_utils.depth_to_pressure(p.z(), p.latitude())

    assert len(t.data) == len(z.data), 'Number of temperature measurements does not equal number of depth measurements.'

    # initialize qc as a bunch of falses;
    # implies all measurements pass when a gradient can't be calculated, such as at edges & gaps in data:
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isPressure = (z.mask==False)
    isData = isTemperature & isPressure

    for i in range(1,len(t.data)-1):
        if isData[i] & isTemperature[i-1] & isTemperature[i+1]:

          isSlope = numpy.abs(t.data[i] - (t.data[i-1] + t.data[i+1])/2)

          if z.data[i] < 500:
              qc[i] = isSlope > 9.0
          else:
              qc[i] = isSlope > 3.0

    return qc
