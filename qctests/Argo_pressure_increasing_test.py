""" 
Implements the pressure increasing check used in the Argo quality control 
system. 

See Argo quality control manual (based on version 2.5),
http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf page 8.
"""

import numpy
from util import obs_utils

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get vertical coordinate values from the profile.
    z = obs_utils.depth_to_pressure(p.z(), p.latitude())

    # Make the quality control decisions. This should
    # return true where z decreases or stays the same.
    qc = numpy.ndarray(p.n_levels(), dtype=bool)
    qc[:] = False
    iRef = -1
    for i in range(0, p.n_levels()):
         # Check if the data value is missing.
         if z.mask[i] == True: 
             continue
         
         # The first level with a z value is saved to use as a reference
         # to compare to the next level.
         if iRef == -1:
             iRef     = i
             zRef     = z[iRef]
             continue
         
         # Check for non-increasing z. If z increases, update the reference.
         if z[i] == zRef:
             qc[i]    = True
         elif z[i] < zRef:
             qc[iRef] = True
             qc[i]    = True
         else:
             iRef     = i
             zRef     = z[iRef]

    return qc


