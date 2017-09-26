
from datetime import datetime
import numpy as np
import math

def haversine(theta):
    '''
    haversine.
    '''

    return math.sin(theta/2)**2

def arcHaversine(hs):
    '''
    inverts haversine
    '''

    sqrths = math.sqrt(hs)
    if sqrths > 1:
        sqrths = round(sqrths, 10)

    return 2 * math.asin(sqrths)

def haversineDistance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    implementation from http://gis.stackexchange.com/questions/44064/how-to-calculate-distances-in-a-point-sequence
    """

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = haversine(dlat) + math.cos(lat1) * math.cos(lat2) * haversine(dlon)
    c = arcHaversine(a) 
    km = 6367 * c
    assert km >= 0, 'haversine returned negative distance'
    return km*1000.

def courseCorrection(lat1, lon1, lat2, lon2, lat3, lon3):
    '''
    Calculate the course correction angle between an initial track from lat/lon1 to lat/lon2,
    and a post-correction track from lat/lon2 and lat/lon3
    return None if any required information is missing.
    '''
    
    if None in [lat1, lon1, lat2, lon2, lat3, lon3]:
        return None

    a = haversineDistance(lat1, lon1, lat2, lon2) / 6367000.
    b = haversineDistance(lat2, lon2, lat3, lon3) / 6367000.
    c = haversineDistance(lat3, lon3, lat1, lon1) / 6367000.

    if a == 0 or b == 0:
        return 0

    cosC = (math.cos(c) - math.cos(a)*math.cos(b))/math.sin(a)/math.sin(b)
    if cosC > 1:
        cosC = 1
    if cosC < -1:
        cosC = -1

    return math.pi - math.acos(cosC)

def deltaTime(earlier, later):
    '''
    Calculate the time difference between two tuples (year, month, day, time),
    in seconds.
    return None if information is missing.
    '''

    if None in [earlier[0], earlier[1], earlier[2], earlier[3]]:
        return None
    if None in [later[0], later[1], later[2], later[3]]:
        return None

    eHour, eMinute, eSecond = parseTime(earlier[3])
    lHour, lMinute, lSecond = parseTime(later[3])

    try:
        early = datetime(year=earlier[0], month=earlier[1], day=earlier[2], hour=eHour, minute=eMinute, second=eSecond )
        late = datetime(year=later[0], month=later[1], day=later[2], hour=lHour, minute=lMinute, second=lSecond )
    except:
        return None

    timeDiff = (late - early).total_seconds()
    assert timeDiff >= 0, 'early date %s is after later date %s' % (early, late)

    return timeDiff

def parseTime(time):
    '''
    convert a WOD time on [0,24) to ints: hour [0,23], minute [0, 59], second [0, 59]
    '''
    hour = np.floor(time)
    minute = np.floor(time*60) % 60
    second = np.floor(time*3600) % 60

    return int(hour), int(minute), int(second)
