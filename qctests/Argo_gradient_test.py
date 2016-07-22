"""
Implements the gradient test on page 8 of http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf
"""

import numpy
from util import obs_utils
import util.main as main

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get temperature values from the profile.
    t = p['t']
    # Get depth values (m) from the profile.
    z = obs_utils.depth_to_pressure(numpy.asarray(p['z']), p['latitude'])

    # initialize qc as a bunch of falses;
    # implies all measurements pass when a gradient can't be calculated, such as at edges & gaps in data:
    qc = numpy.zeros(p['n_levels'], dtype=bool)

    for i in range(1,p['n_levels']-1):
        if main.dataPresent(('t', 'z'), i, p) and main.dataPresent(('t'), i-1, p) and main.dataPresent(('t'), i+1, p):

          isSlope = numpy.abs(t[i] - (t[i-1] + t[i+1])/2)

          if z[i] < 500:
              qc[i] = isSlope > 9.0
          else:
              qc[i] = isSlope > 3.0

    return qc
