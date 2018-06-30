# spike test adpated from Patrick Halsall's 
# ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/codes/qc_checks/spike_checker.py
# cal

import numpy

def test(p, parameters):

    qc = numpy.zeros(p.n_levels(), dtype=bool)

    t = p.t()

    for i in range(2, p.n_levels()-2):
        qc[i] = spike(t[i-2:i+3])

    qc[1] = spike(t[0:3])
    qc[-2] = spike(t[-3:])

    return qc

def spike(t):
	# generic spike check for a masked array of an odd number of consecutive temperature measurements

    if True in t.mask:
    	# missing data, decline to flag
    	return False

    centralTemp = t[int(len(t)/2)]
    medianDiff = round( abs(centralTemp - numpy.median(t)),2)

    if medianDiff != 0:
    	t = numpy.delete(t, int(len(t)/2))
    	spikeCheck = round(abs(centralTemp-numpy.mean(t)), 2)
    	if spikeCheck > 0.3:
            return True

    return False





