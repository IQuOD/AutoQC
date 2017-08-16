"""
Implements CSIRO's long gradient check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # depths
    d = p.z()
    # temperatures
    t = p.t()

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)
    isTemperature = (t.mask==False)
    isData = isTemperature & isDepth

    on_inv = False # are we currently in an inversion?

    for i in range(0, p.n_levels()-1 ):
        if isData[i] and isData[i+1]:
            # not interested below 5m:
            if d.data[i] < 5: continue

            if t.data[i+1] > t.data[i] and not on_inv:
                # entering an inversion
                start_inv_temp = t.data[i]
                start_inv_depth = d.data[i]
                potential_flag = i
                on_inv = True

            if t.data[i+1] < t.data[i] and on_inv:
                # exiting the inversion
                end_inv_temp = t.data[i]
                end_inv_depth = d.data[i]
                on_inv = False
                gradlong = (end_inv_depth - start_inv_depth) / (end_inv_temp - start_inv_depth)

                if abs(gradlong) < 4:
                    qc[potential_flag] = True

    return qc
