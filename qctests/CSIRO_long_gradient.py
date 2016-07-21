"""
Implements CSIRO's long gradient check
All questionable features result in a flag, in order to minimize false negatives 
"""

import numpy
import util.main as main

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # depths
    d = p['z']
    # temperatures
    t = p['t']

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t), dtype=bool)

    on_inv = False # are we currently in an inversion?

    for i in range(0, p['n_levels']-1 ):
       if main.dataPresent(('t', 'z'), i, p) and main.dataPresent(('t', 'z'), i+1, p): 
            # not interested below 5m:
            if d[i] < 5: continue

            if t[i+1] > t[i] and not on_inv:
                # entering an inversion
                start_inv_temp = t[i]
                start_inv_depth = d[i]
                potential_flag = i
                on_inv = True

            if t[i+1] < t[i] and on_inv:
                # exiting the inversion
                end_inv_temp = t[i]
                end_inv_depth = d[i]
                on_inv = False
                gradlong = (end_inv_depth - start_inv_depth) / (end_inv_temp - start_inv_depth)

                if abs(gradlong) < 4:
                    qc[potential_flag] = True

    return qc
