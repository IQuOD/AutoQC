"""
Implements the regional range test on page 7 of http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf
"""

import numpy, pyproj
from shapely.geometry import Polygon, Point

def test(p, parameters):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    redSeaLat  = [10., 20., 30., 10.]
    redSeaLong = [40., 50., 30., 40.]

    mediterraneanLat  = [30., 30., 40., 42., 50., 40., 30]
    mediterraneanLong = [6.,  40., 35., 20., 15., 5.,  6.]

    # Get the lat and long and temp:
    latitude = p.latitude()
    longitude = p.longitude()
    t = p.t()

    # check for gaps in data
    isTemperature = (t.mask==False)

    # initialize qc as false (all pass)
    qc = numpy.zeros(len(t), dtype=bool)

    isInRedSea = isInRegion(latitude, longitude, redSeaLat, redSeaLong)
    isInMediterranean = isInRegion(latitude, longitude, mediterraneanLat, mediterraneanLong)

    for i in range(p.n_levels()):
        if isTemperature[i]:
            if isInRedSea:
                if t[i] < 21.7 or t[i] > 40.:
                    qc[i] = True
            if isInMediterranean:
                if t[i] < 10. or t[i] > 40.:
                    qc[i] = True

    return qc

def isInRegion(lat, longitude, regionLat, regionLong):
    '''
    determine if the point lat, longitude is in the region bounded by a polygon with vertices regionLat, regionLong
    adapted from solution at http://gis.stackexchange.com/questions/79215/determine-if-point-is-within-an-irregular-polygon-using-python
    '''

    # WGS84 datum                                                               
    wgs84 = pyproj.Proj(init='EPSG:4326')                                       

    # Albers Equal Area Conic (aea)                                             
    nplaea = pyproj.Proj("+proj=laea +lat_0=90 +lon_0=-40 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    # Transform polygon and test point coordinates to northern lat AEAC projection    
    poly_x, poly_y = pyproj.transform(wgs84, nplaea, regionLong, regionLat)      
    point_x, point_y = pyproj.transform(wgs84, nplaea, [longitude], [lat])

    poly_proj = Polygon(zip(poly_x,poly_y))

    testPoint = Point(point_x[0], point_y[0])
    return testPoint.within(poly_proj)


