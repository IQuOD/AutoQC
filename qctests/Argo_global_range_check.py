""" 
Implements the global range check used in the Argo quality control 
system. 

See Argo quality control manual (based on version 2.5).
"""

from util import obs_utils
import util.main as main
import numpy

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get temperature and pressure values from the profile.
    t = p['t']
    z = obs_utils.depth_to_pressure(numpy.asarray(p['z']), p['latitude'])

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(p['n_levels'], dtype=bool)
    
    # Make the quality control decisions. This should
    # return true if the temperature is outside -2.5 deg C
    # and 40 deg C or pressure is less than -5.
    for i in range(p['n_levels']):
        if main.dataPresent(('t'), i, p):
            qc[i] == t[i] > -2.5 and t[i] < 40.0
        if main.dataPresent(('z', 'latitude'), i, p):
           qc[i] == qc[i] and z[i] > -5

    return qc


