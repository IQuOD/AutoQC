"""
Implements the wire break test of https://github.com/BecCowley/Mquest/blob/083b9a3dc7ec9076705aca0e90bcb500d241be03/GUI/detectwirebreak.m
"""

import numpy

def istight(t, thresh=0.1):
    # given a temperature profile, return an array of bools
    # true = this level is within thresh of both its neighbors
    gaps = numpy.absolute(numpy.diff(t))
    left = numpy.append(gaps,0)
    right = numpy.insert(gaps,0,0)
    return (left<thresh) & (right<thresh)

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    t = p.t()

    # initialize qc as a bunch of falses:
    qc = numpy.zeros(len(t.data), dtype=bool)

    # only meaningful for XBT data
    if p.probe_type() != 2:
        return qc

    no_wb = numpy.where( (t >= -2.4) & (t <= 32) & istight(t) )[0]

    if len(no_wb) > 0:
        last_good = no_wb[-1]
        qc = numpy.append(numpy.zeros(last_good + 1, dtype=bool), numpy.ones(len(t) - last_good - 1, dtype=bool))
    else:
        qc = numpy.ones(len(t.data), dtype=bool)

    return qc


