# gross range test adpated from Patrick Halsall's 
# ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/codes/qc_checks/gross_checker.py

import numpy

def test(p, parameters):

    qc = numpy.zeros(p.n_levels(), dtype=bool)
    t = p.t()
    z = p.z()
    isTemperature = (t.mask==False)
    isDepth = (z.mask==False)

    for i in range(p.n_levels()):
    	if isTemperature[i] and not (-2.5 <= t[i] <= 40):
            qc[i] = True
        if isDepth[i] and not (0 <= z[i] <= 2000):
            qc[i] = True

    return qc