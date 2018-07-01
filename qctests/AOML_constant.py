# constant value test adpated from Patrick Halsall's 
# ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/codes/qc_checks/constant_checker.py

import numpy

def test(p, parameters):

    qc = numpy.zeros(p.n_levels(), dtype=bool)
    t = p.t()

    # make sure there's more than one unmasked temperature
    unmasked_t = [q for q in t if not numpy.ma.is_masked(q) ]
    if len(unmasked_t) == 1:
        return qc

    unique_t = set(unmasked_t)
    if len(unique_t) == 1:
        return numpy.ones(p.n_levels(), dtype=bool)

    return qc