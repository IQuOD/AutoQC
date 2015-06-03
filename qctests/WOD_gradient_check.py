"""
Implements the excessive gradient test on page 47 of http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
"""

import numpy

def test(p, **kwargs):
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
    # implies all measurements pass when a gradient can't be calculated, such as at edges & gaps in data:
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)
    isData = isTemperature & isDepth

    for i in range(0,len(t.data)-1):
        if isData[i] & isData[i+1] & (d.data[i+1] - d.data[i] > 0):

          gradient = (t.data[i+1] - t.data[i]) / max([ (d.data[i+1] - d.data[i]) , 3.0])

          # gradient & inversion check
          qc[i] = (gradient > 0.3) or (gradient < -0.7) or qc[i] # in case qc[i] was set true by the zero sensitivity indicator in the previous step
          qc[i+1] = (gradient > 0.3) or (gradient < -0.7)

          # zero sensitivity indicator
          # flags data if temperature drops to 0 too abruptly, indicating a missing value.
          if t.data[i+1] == 0:
              if -1.0 * gradient > 5.0 * 0.7:
                  qc[i+1] = True

    return qc
