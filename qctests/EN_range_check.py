""" 
Implements the global range check used in the EN quality control 
system. 
"""

import numpy as np

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. The profile object p must 
    have a method t() that returns a numpy masked array of temperature 
    values. 
    """

    # Get temperature values from the profile.
    t = p.t()

    # Make the quality control decisions. This should
    # return true if the temperature is outside -4 deg C
    # and 40 deg C.
    qc = (t.mask == False) & ((t.data < -4.0) | (t.data > 40.0))

    return qc

if __name__ == '__main__':
    # Example of the use the quality control check.

    # Set up a class that emulates the methods provided by the
    # WodProfile class.
    class dummyClass(object):
        # The z method returns an array of depth values.
        def z(self): return np.ma.array([0.0, 10.0, 50.0, 100.0], 
                                        mask=False)
        # The t method returns an array of temperature values
        # corresponding to the depths defined above. 
        def t(self): return np.ma.array([0.0, -10.0, 43.0, 40.0],
                                        mask=False)

    # Run the quality control check on the dummy data.
    profile = dummyClass()
    result  = test(profile)

    # Print the result.
    print(profile.t())
    print(result)

