
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

def haversineDistance(pro1, pro2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    implementation from http://gis.stackexchange.com/questions/44064/how-to-calculate-distances-in-a-point-sequence
    """

    lon1 = pro1.longitude()
    lat1 = pro1.latitude()
    lon2 = pro2.longitude()
    lat2 = pro2.latitude()

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

def haversineAngle(pro1, pro2, pro3):
    '''
    Calculate the angle subtended by the great circle passing through pro1 and pro2,
    with that passing through pro2 and pro3 (all the pro* are WOD profiles or headers)
    return None if any required information is missing.
    '''

    if None in [pro1.latitude(), pro1.longitude()]:
        return None
    if None in [pro2.latitude(), pro2.longitude()]:
        return None
    if None in [pro3.latitude(), pro3.longitude()]:
        return None

    a = haversineDistance(pro1, pro2) / 6367000.
    b = haversineDistance(pro2, pro3) / 6367000.
    c = haversineDistance(pro3, pro1) / 6367000.

    if a == 0 or b == 0:
        return 0

    C = arcHaversine( (haversine(c) - haversine(a-b)) / math.sin(a) / math.sin(b) )

    return C

def deltaTime(earlier, later):
    '''
    Calculate the time difference between two profiles, later and earlier,
    in seconds.
    return None if information is missing.
    '''

    if None in [earlier.year(), earlier.month(), earlier.day(), earlier.time()]:
        return None
    if None in [later.year(), later.month(), later.day(), later.time()]:
        return None

    eHour, eMinute, eSecond = parseTime(earlier.time())
    lHour, lMinute, lSecond = parseTime(later.time())

    early = datetime(year=earlier.year(), month=earlier.month(), day=earlier.day(), hour=eHour, minute=eMinute, second=eSecond )
    late = datetime(year=later.year(), month=later.month(), day=later.day(), hour=lHour, minute=lMinute, second=lSecond )

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