""" 
Implements the EN track check, described on pp 7 and 21 of
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import numpy as np
import data.ds as ds
import util.main as main
import util.geo as geo
import copy
import datetime
import math

# module constants
DistRes = 20000. # meters
TimeRes = 600. # seconds

EN_track_headers = {}
EN_track_results = {}

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    global EN_track_headers
    global EN_track_results

    cruise = p.cruise()
    uid = p.uid()

    # don't bother if cruise == 0 or None
    if cruise in [0, None]:
        return np.zeros(1, dtype=bool);

    # The headers from an entire cruise must be analyzed all at once;
    # we'll write the results to the global data store, in a dictionary
    # with ntuple keys (cruise, uid), and values as single element
    # numpy arrays, containing either a true or a false (per all the other
    # qc return objects) 

    # check if this profile has been examined already
    if (cruise, uid) in EN_track_results.keys():
        return EN_track_results[(cruise, uid)]

    # some detector types cannot be assessed by this test; do not raise flag.
    if p.probe_type in [None]:
        return np.zeros(1, dtype=bool)

    # the first time this test is run, sort ds.threadProfiles into a cruise-keyed dictionary:
    if EN_track_headers == {}:
        EN_track_headers = main.sort_headers(ds.threadProfiles)

    # since we didn't find an answer already calculated,
    # we still need to do the calculation for this cruise;
    # all the relevant headers are sitting in the EN_track_headers list.
    headers = EN_track_headers[cruise]

    # start all as passing by default:
    for i in range(len(headers)):
        EN_track_results[(headers[i].cruise(), headers[i].uid())] = np.zeros(1, dtype=bool)

    # copy the list of headers;
    # remove entries as they are flagged.
    passedHeaders = copy.deepcopy(headers)
    rejects = findOutlier(passedHeaders)
    while rejects != []:
        passedIndex = [x for x in range(len(passedHeaders)) if x not in rejects ]
        passedHeaders = [passedHeaders[index] for index in passedIndex ]
        rejects = findOutlier(passedHeaders)

    # if more than half got rejected, reject everyone
    if len(passedHeaders) < len(headers) / 2:
        for i in range(len(headers)):
            EN_track_results[(headers[i].cruise(), headers[i].uid())][0] = True        

    return EN_track_results[(cruise, uid)]

def findOutlier(headers):
    '''
    given a list of <headers>, find the fastest one;
    if it's too fast, reject it or the one before it, return a list of rejected indices;
    once the fastest is within limits, return [].
    '''

    maxShipSpeed = 15. # m/s
    maxBuoySpeed = 2. # m/s

    if headers == []:
        return []

    # determine speeds and angles for list of headers
    speeds, angles = calculateTraj(headers)

    # decide if something needs to be flagged
    maxSpeed = maxShipSpeed
    if isBuoy(headers[0]):
        maxSpeed = maxBuoySpeed
    iMax = speeds.index(max(speeds))
    flag = detectExcessiveSpeed(speeds, angles, iMax, maxSpeed)

    # decide which profile to reject, flag it, and return a list of indices rejected at this step.
    if flag:
        rejects = chooseReject(headers, speeds, angles, iMax, maxSpeed)

        for reject in rejects:
            EN_track_results[(headers[reject].cruise(), headers[reject].uid())][0] = True
        return rejects
    else:
        return []

def chooseReject(headers, speeds, angles, index, maxSpeed):
    '''
    decide which profile to reject, headers[index] or headers[index-1], or both,
    and return a list of indices to reject.
    '''

    # chain of tests breaks when a reject is found:
    reject = condition_a(headers, speeds, angles, index, maxSpeed)[0]

    # condition i needs to run at the end of the chain in all cases:
    # if no decision, reject both:
    if reject == -1:
        reject = [index-1, index]
    # if excessive speed is created by removing the flag, reject both instead 
    # can't create new excessive speed by removing last profile.
    elif reject < len(headers)-1: 
        newHeaders = copy.deepcopy(headers)
        del newHeaders[reject]
        newSpeeds, newAngles = calculateTraj(newHeaders)
        flag = detectExcessiveSpeed(newSpeeds, newAngles, reject, maxSpeed)
        if flag:
            reject = [index-1, index]
        else:
            reject = [reject]
    else:
        reject = [reject]

    return reject

def calculateTraj(headers):
    '''
    return a list of speeds and a list of angles describing the trajectory of the track described
    by the time-ordered list of <headers>.
    '''

    speeds = [None]
    angles = [None]

    # Find speed and angle for all profiles remaining in the list
    for i in range(1, len(headers)):

        speeds.append(None)
        angles.append(None)

        speeds[i] = trackSpeed(headers[i-1], headers[i])
        if i < len(headers)-1: # can't do angle on last point 
            angles[i] = abs(math.pi - geo.haversineAngle(headers[i-1], headers[i], headers[i+1]))

    return speeds, angles

def isBuoy(header):
    '''
    decide if header belongs to a buoy-based measurement
    '''

    return header.probe_type in [4,7,9,10,11,12,13,15]

def detectExcessiveSpeed(speeds, angles, index, maxSpeed):
    '''
    decide if there was an excessive speed at <index> in the lists <speeds> and <angles>
    '''

    flag = speeds[index] > maxSpeed

    if index > 0:
        flag = flag or ( (speeds[index] > 0.8*maxSpeed) and (angles[index]>math.pi/2 or angles[index-1]>math.pi/2) )

    return flag

def meanSpeed(speeds, headers, maxSpeed):
    '''
    determine mean speed, neglecting missing data, intervals less than 1h, and speeds over maxspeed, for use in condition (f)
    '''

    meanSpeed = 0
    speedCount = 0
    for iSpeed, speed in enumerate(speeds):
        if speed == None or iSpeed == 0:
            #missing values
            continue
        elif iSpeed > 0 and geo.deltaTime(headers[iSpeed-1], headers[iSpeed]) < 3600.:
            #too close together in time
            continue
        elif speed > maxSpeed:
            #too fast
            continue
        else:
            meanSpeed += speed
            speedCount += 1

    if speedCount > 0:
        meanSpeed = meanSpeed / speedCount

    return meanSpeed


def trackSpeed(prevHeader, header):
    '''
    computes the speed, including rounding tolerance from the reference,
    for the track at <header>.
    return None if some necessary data is missing
    '''

    # check that all required data is present:
    if None in [header.latitude(), header.longitude(), prevHeader.latitude(), prevHeader.longitude()]:
        return None
    if None in [header.year(), header.month(), header.day(), header.time(), prevHeader.year(), prevHeader.month(), prevHeader.day(), prevHeader.time()]:
        return None

    dist = geo.haversineDistance(prevHeader, header)
    DTime = geo.deltaTime(prevHeader, header)
    speed = (dist - DistRes) / max(DTime, TimeRes)

    return speed

def condition_a(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (a) from the text
    '''

    if index == 1 and len(headers) == 2:
        return 0, 'a'
    elif index == 1 and len(headers) > 2: # note 'M' in the text seems to count from 1, not 0.
        impliedSpeed = trackSpeed(headers[0], headers[2])
        if impliedSpeed < maxSpeed and (speeds[2]>maxSpeed or angles[2]>45./180.*math.pi):
            return 1, 'a'
        else:
            return 0, 'a'
    elif index == len(headers)-1 and len(headers)>3:  # why not >=? seems to cause problems, investigate.
        impliedSpeed = trackSpeed(headers[-3], headers[-1])
        if impliedSpeed < maxSpeed and (speeds[-2] > maxSpeed or angles[-3]>45./180.*math.pi):
            return index-1, 'a'
        else:
            return index, 'a'
    else:
        return condition_b(headers, speeds, angles, index, maxSpeed)

def condition_b(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (b) from the text
    '''
    if speeds[index-1] > maxSpeed:
        return index-1, 'b'
    elif index < len(speeds) - 1 and speeds[index+1] > maxSpeed:
        return index, 'b'

    return condition_c(headers, speeds, angles, index, maxSpeed)

def condition_c(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (c) from the text
    '''

    if index < len(headers)-1 and index > 0:
        impliedSpeed = trackSpeed(headers[index-1], headers[index+1])
        if impliedSpeed > maxSpeed:
            return index-1, 'c'

    if index > 1:
        impliedSpeed = trackSpeed(headers[index-2], headers[index])
        if impliedSpeed > maxSpeed:
            return index, 'c'

    return condition_d(headers, speeds, angles, index, maxSpeed)


def condition_d(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (d) from the text
    '''

    if None not in [angles[index-1], angles[index]] and angles[index-1] > 45./180.*math.pi + angles[index]:
        return index-1, 'd'

    if None not in [angles[index-1], angles[index]] and angles[index] > 45./180.*math.pi + angles[index-1]:
        return index, 'd'

    return condition_e(headers, speeds, angles, index, maxSpeed)

def condition_e(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (e) from the text
    '''

    if len(headers) > max(2, index+1):

        if None not in [angles[index-2], angles[index+1]] and angles[index-2] > 45./180.*math.pi and angles[index-2] > angles[index+1]:
            return index-1, 'e'

        if None not in [angles[index+1]] and angles[index+1] > 45./180.*math.pi:
            return index, 'e'

    return condition_f(headers, speeds, angles, index, maxSpeed)

def condition_f(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (f) from the text
    '''

    if index>0 and index < len(speeds)-1:

        ms = meanSpeed(speeds, headers, maxSpeed)

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index-1] < min([speeds[index+1], 0.5*ms]):
            return index-1, 'f'

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index+1] < min([speeds[index-1], 0.5*ms]):
            return index, 'f'

    return condition_g(headers, speeds, angles, index, maxSpeed)

def condition_g(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (g) from the text
    '''

    if index > 1 and index < len(headers) - 1:
    
        dist1 = geo.haversineDistance(headers[index], headers[index-2]) + geo.haversineDistance(headers[index + 1], headers[index])
        dist2 = geo.haversineDistance(headers[index-1], headers[index-2]) + geo.haversineDistance(headers[index + 1], headers[index-1])

        distTol = geo.haversineDistance(headers[index-1], headers[index-2])
        distTol += geo.haversineDistance(headers[index], headers[index-1])
        distTol += geo.haversineDistance(headers[index+1], headers[index])
        distTol = max(DistRes, 0.1*distTol)

        if dist1 < dist2 - distTol:
            return index-1, 'g'

        if dist2 < dist1 - distTol:
            return index, 'g'

    return condition_h(headers, speeds, angles, index, maxSpeed)

def condition_h(headers, speeds, angles, index, maxSpeed):
    '''
    assess condition (h) from the text
    typeo in text, implementation incomplete
    '''
    
    if index > 1 and index < len(headers) - 1:

        dist1 = geo.haversineDistance(headers[index], headers[index-2]) + geo.haversineDistance(headers[index + 1], headers[index])
        dist2 = geo.haversineDistance(headers[index-1], headers[index-2]) + geo.haversineDistance(headers[index + 1], headers[index-1])

        PD1 = geo.haversineDistance(headers[index-1], headers[index-2]) / dist2
        PD2 = geo.haversineDistance(headers[index], headers[index-2]) / dist1

        PT1 = geo.deltaTime(headers[index-2], headers[index-1]) / geo.deltaTime(headers[index-2], headers[index+1])
        PT2 = geo.deltaTime(headers[index-2], headers[index]) / geo.deltaTime(headers[index-2], headers[index+1])

        if abs(PD1-PT1) > 0.1 + abs(PD2-PT2):
            return index-1, 'h'
        if abs(PD2 - PT2) > 0.1 + abs(PD1 - PT1):
            return index, 'h'

    return -1, 'i'

def checkOrder(profiles):
    '''
    check that a list of profiles is properly time ordered
    '''

    dates = []
    for pro in profiles:
        if pro.time() is not None:
            hour, minute, second = geo.parseTime(pro.time())
        else:
            hour = 0
            minute = 0
            second = 0
        date = datetime.datetime(year=pro.year(), month=pro.month(), day=pro.day(), hour=hour, minute=minute, second=second )
        dates.append(date)

    for i in range(len(dates)-1):
        assert dates[i] <= dates [i+1], 'dates out of order %s %s' % (dates[i], dates[i+1])
