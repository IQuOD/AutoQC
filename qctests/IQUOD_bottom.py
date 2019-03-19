import numpy
import util.main as main
from netCDF4 import Dataset

def test(p, parameters):

    # register bathymetry data in parameters object on first use
    if 'bathymetry' not in parameters:
        print 'extracting bathymetry'
        nc = Dataset('data/ETOPO1_Bed_g_gmt4.grd')
        parameters['bathymetry'] = {}
        parameters['bathymetry']['longitude'] = nc.variables['x'][:]
        parameters['bathymetry']['latitude'] = nc.variables['y'][:]
        parameters['bathymetry']['depth'] = nc.variables['z'][:]

    d = p.z()
    lat = p.latitude()
    lon = p.longitude()

    # get ocean depth at this point
    floor = -1.0*main.find_depth(lat, lon, parameters['bathymetry'])

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(p.n_levels(), dtype=bool)

    # check for gaps in data
    isDepth = (d.mask==False)

    for i in range(p.n_levels()):
        if isDepth[i]:
            qc[i] = d[i] > floor

    return qc