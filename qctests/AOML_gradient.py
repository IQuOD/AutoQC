# gradient test adpated from Patrick Halsall's 
# ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/codes/qc_checks/vertical_gradient_checker.py

import numpy

def test(p, parameters):

    qc = numpy.zeros(p.n_levels(), dtype=bool)

    t = p.t()
    z = p.z()

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (z.mask==False)
    isData = isTemperature & isDepth

    for i in range(p.n_levels()-1):
        if isData[i] and isData[i+1]:
            gradTest = (t[i+1]-t[i]) / (z[i+1]-z[i])
            if t[i+1]-t[i] < 0 and abs(gradTest) > 1.0:
                qc[i] = True
            elif gradTest > 0.2:
                qc[i] = True

    return qc
