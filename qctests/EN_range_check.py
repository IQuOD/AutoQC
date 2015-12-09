""" 
Implements the global range check used in the EN quality control 
system. 
"""

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get temperature values from the profile.
    t = p.t()

    # Make the quality control decisions. This should
    # return true if the temperature is outside -4 deg C
    # and 40 deg C.
    qc = (t.mask == False) & ((t.data < -4.0) | (t.data > 40.0))

    return qc


