import numpy
import util.main as main

def test(p, parameters):

    d = p.z()
    lat = p.latitude()
    lon = p.longitude()

    # get ocean depth at this point
    floor = -1.0*main.find_depth(lat, lon)

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(p.n_levels(), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)

    for i in range(p.n_levels()):
        if isDepth[i]:
            qc[i] = d[i] > floor

    return qc