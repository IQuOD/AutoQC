""" 
Implements the EN track check, described on pp 7 and 21 of
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import numpy as np
import util.main as main
import util.geo as geo
import copy, datetime, math, psycopg2
import sys

# module constants
DistRes = 20000. # meters
TimeRes = 600. # seconds

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """
    
    conn = psycopg2.connect("dbname='root' user='root'")
    conn.autocommit = True
    cur = conn.cursor()
   
    cruise = p.cruise()
    uid = p.uid()
    
    # don't bother if cruise == 0 or None
    if cruise in [0, None]:
        return np.zeros(1, dtype=bool)

    # don't bother if this has already been analyzed
    # cur.execute('SELECT en_track_check FROM ' + sys.argv[1] + ' WHERE uid = ' + str(uid) + ';')
    # en_track_result = cur.fetchall()
    # if en_track_result[0][0] is not None:
    #   result = np.zeros(1, dtype=bool)
    #   result[0] = en_track_result[0][0]
    #   return result

    # some detector types cannot be assessed by this test; do not raise flag.
    if p.probe_type in [None]:
        return np.zeros(1, dtype=bool)

    # fetch all profiles on track, sorted chronologically, earliest first (None sorted as highest)
    cur.execute('SELECT raw FROM ' + sys.argv[1] + ' WHERE cruise = ' + str(cruise) + 'ORDER BY year, month, day, time ASC;')
    track_rows = cur.fetchall()
    track_profiles = [main.text2wod(raw[0]) for raw in track_rows]

    # start all as passing by default:
    EN_track_results = {}
    for i in range(len(track_profiles)):
        EN_track_results[track_profiles[i].uid()] = np.zeros(1, dtype=bool)

    # copy the list of headers;
    # remove entries as they are flagged.
    passed_profiles = copy.deepcopy(track_profiles)
    rejects = findOutlier(passed_profiles, EN_track_results)
    
    while rejects != []:
        passed_index = [x for x in range(len(passed_profiles)) if x not in rejects ]
        passed_profiles = [passed_profiles[index] for index in passed_index ]
        rejects = findOutlier(passed_profiles, EN_track_results)

    # if more than half got rejected, reject everyone
    if len(passed_profiles) < len(track_rows) / 2:
        for i in range(len(track_profiles)):
            EN_track_results[track_profiles[i].uid()][0] = True

    # write all to db
    for i in range(len(track_profiles)):
        query = "UPDATE " + sys.argv[1] + " SET en_track_check " + " = " + str(EN_track_results[track_profiles[i].uid()][0]) + " WHERE uid = " + str(track_profiles[i].uid()) + ";"
        main.dbinteract(query)

    return EN_track_results[uid]

def findOutlier(profiles, results):
    '''
    given a list of profiles, find the fastest one;
    if it's too fast, reject it or the one before it, return a list of rejected indices;
    once the fastest is within limits, return [].
    '''

    maxShipSpeed = 15. # m/s
    maxBuoySpeed = 2. # m/s

    if profiles == []:
        return []

    # determine speeds and angles for list of headers
    speeds, angles = calculateTraj(profiles)
  
    # decide if something needs to be flagged
    maxSpeed = maxShipSpeed
    if isBuoy(profiles[0]):
        maxSpeed = maxBuoySpeed
    iMax = speeds.index(max(speeds))
    flag = detectExcessiveSpeed(speeds, angles, iMax, maxSpeed)

    # decide which profile to reject, flag it, and return a list of indices rejected at this step.
    if flag:
        rejects = chooseReject(profiles, speeds, angles, iMax, maxSpeed)
        for reject in rejects:
            results[profiles[reject].uid()][0] = True
        return rejects
    else:
        return []

def chooseReject(profiles, speeds, angles, index, maxSpeed):
    '''
    decide which profile to reject, profiles[index] or profiles[index-1], or both,
    and return a list of indices to reject.
    '''

    # chain of tests breaks when a reject is found:
    reject = condition_a(profiles, speeds, angles, index, maxSpeed)[0]

    # condition i needs to run at the end of the chain in all cases:
    # if no decision, reject both:
    if reject == -1:
        reject = [index-1, index]
    # if excessive speed is created by removing the flag, reject both instead 
    # can't create new excessive speed by removing last profile.
    elif reject < len(profiles)-1: 
        new_profiles = copy.deepcopy(profiles)
        del new_profiles[reject]
        newSpeeds, newAngles = calculateTraj(new_profiles)
        flag = detectExcessiveSpeed(newSpeeds, newAngles, reject, maxSpeed)
        if flag:
            reject = [index-1, index]
        else:
            reject = [reject]
    else:
        reject = [reject]

    return reject

def calculateTraj(profiles):
    '''
    return a list of speeds and a list of angles describing the trajectory of the track described
    by the time-ordered list of profiles.
    '''

    speeds = [None]
    angles = [None]

    # Find speed and angle for all profiles remaining in the list
    for i in range(1, len(profiles)):

        speeds.append(None)
        angles.append(None)
        speeds[i] = trackSpeed(profiles[i-1], profiles[i])

        if i < len(profiles)-1: # can't do angle on last point 
            angles[i] = abs(math.pi - geo.haversineAngle(profiles[i-1], profiles[i], profiles[i+1]))

    return speeds, angles

def isBuoy(profile):
    '''
    decide if profile belongs to a buoy-based measurement
    '''
    return profile.probe_type() in [4,7,9,10,11,12,13,15]

def detectExcessiveSpeed(speeds, angles, index, maxSpeed):
    '''
    decide if there was an excessive speed at <index> in the lists <speeds> and <angles>
    '''

    flag = speeds[index] > maxSpeed

    if index > 0:
        flag = flag or ( (speeds[index] > 0.8*maxSpeed) and (angles[index]>math.pi/2 or angles[index-1]>math.pi/2) )

    return flag

def meanSpeed(speeds, profiles, maxSpeed):
    '''
    determine mean speed, neglecting missing data, intervals less than 1h, and speeds over maxspeed, for use in condition (f)
    '''

    meanSpeed = 0
    speedCount = 0
    for iSpeed, speed in enumerate(speeds):
        if speed == None or iSpeed == 0:
            #missing values
            continue
        elif iSpeed > 0 and geo.deltaTime(profiles[iSpeed-1], profiles[iSpeed]) < 3600.:
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


def trackSpeed(prev_profile, profile):
    '''
    computes the speed, including rounding tolerance from the reference,
    for the track at <profile>.
    return None if some necessary data is missing
    '''

    # check that all required data is present:
    if None in [profile.latitude(), profile.longitude(), prev_profile.latitude(), prev_profile.longitude()]:
        return None
    if None in [profile.year(), profile.month(), profile.day(), profile.time(), prev_profile.year(), prev_profile.month(), prev_profile.day(), prev_profile.time()]:
        return None

    dist = geo.haversineDistance(prev_profile, profile)
    DTime = geo.deltaTime(prev_profile, profile)
    speed = (dist - DistRes) / max(DTime, TimeRes)

    return speed

def condition_a(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (a) from the text
    '''

    if index == 1 and len(profiles) == 2:
        return 0, 'a'
    elif index == 1 and len(profiles) > 2: # note 'M' in the text seems to count from 1, not 0.
        impliedSpeed = trackSpeed(profiles[0], profiles[2])
        if impliedSpeed < maxSpeed and (speeds[2]>maxSpeed or angles[2]>45./180.*math.pi):
            return 1, 'a'
        else:
            return 0, 'a'
    elif index == len(profiles)-1 and len(profiles)>3:  # why not >=? seems to cause problems, investigate.
        impliedSpeed = trackSpeed(profiles[-3], profiles[-1])
        if impliedSpeed < maxSpeed and (speeds[-2] > maxSpeed or angles[-3]>45./180.*math.pi):
            return index-1, 'a'
        else:
            return index, 'a'
    else:
        return condition_b(profiles, speeds, angles, index, maxSpeed)

def condition_b(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (b) from the text
    '''

    if speeds[index-1] > maxSpeed:
        return index-1, 'b'
    elif index < len(speeds) - 1 and speeds[index+1] > maxSpeed:
        return index, 'b'

    return condition_c(profiles, speeds, angles, index, maxSpeed)

def condition_c(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (c) from the text
    '''

    if index < len(profiles)-1 and index > 0:
        impliedSpeed = trackSpeed(profiles[index-1], profiles[index+1])
        if impliedSpeed > maxSpeed:
            return index-1, 'c'

    if index > 1:
        impliedSpeed = trackSpeed(profiles[index-2], profiles[index])
        if impliedSpeed > maxSpeed:
            return index, 'c'

    return condition_d(profiles, speeds, angles, index, maxSpeed)


def condition_d(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (d) from the text
    '''

    if None not in [angles[index-1], angles[index]] and angles[index-1] > 45./180.*math.pi + angles[index]:
        return index-1, 'd'

    if None not in [angles[index-1], angles[index]] and angles[index] > 45./180.*math.pi + angles[index-1]:
        return index, 'd'

    return condition_e(profiles, speeds, angles, index, maxSpeed)

def condition_e(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (e) from the text
    '''

    if len(profiles) > max(2, index+1):

        if None not in [angles[index-2], angles[index+1]] and angles[index-2] > 45./180.*math.pi and angles[index-2] > angles[index+1]:
            return index-1, 'e'

        if None not in [angles[index+1]] and angles[index+1] > 45./180.*math.pi:
            return index, 'e'

    return condition_f(profiles, speeds, angles, index, maxSpeed)

def condition_f(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (f) from the text
    '''

    if index>0 and index < len(speeds)-1:

        ms = meanSpeed(speeds, profiles, maxSpeed)

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index-1] < min([speeds[index+1], 0.5*ms]):
            return index-1, 'f'

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index+1] < min([speeds[index-1], 0.5*ms]):
            return index, 'f'

    return condition_g(profiles, speeds, angles, index, maxSpeed)

def condition_g(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (g) from the text
    '''

    if index > 1 and index < len(profiles) - 1:
    
        dist1 = geo.haversineDistance(profiles[index], profiles[index-2]) + geo.haversineDistance(profiles[index + 1], profiles[index])
        dist2 = geo.haversineDistance(profiles[index-1], profiles[index-2]) + geo.haversineDistance(profiles[index + 1], profiles[index-1])

        distTol = geo.haversineDistance(profiles[index-1], profiles[index-2])
        distTol += geo.haversineDistance(profiles[index], profiles[index-1])
        distTol += geo.haversineDistance(profiles[index+1], profiles[index])
        distTol = max(DistRes, 0.1*distTol)

        if dist1 < dist2 - distTol:
            return index-1, 'g'

        if dist2 < dist1 - distTol:
            return index, 'g'

    return condition_h(profiles, speeds, angles, index, maxSpeed)

def condition_h(profiles, speeds, angles, index, maxSpeed):
    '''
    assess condition (h) from the text
    '''
    
    if index > 1 and index < len(profiles) - 1:

        dist1 = geo.haversineDistance(profiles[index], profiles[index-2]) + geo.haversineDistance(profiles[index + 1], profiles[index])
        dist2 = geo.haversineDistance(profiles[index-1], profiles[index-2]) + geo.haversineDistance(profiles[index + 1], profiles[index-1])

        PD1 = geo.haversineDistance(profiles[index-1], profiles[index-2]) / dist2
        PD2 = geo.haversineDistance(profiles[index], profiles[index-2]) / dist1

        PT1 = geo.deltaTime(profiles[index-2], profiles[index-1]) / geo.deltaTime(profiles[index-2], profiles[index+1])
        PT2 = geo.deltaTime(profiles[index-2], profiles[index]) / geo.deltaTime(profiles[index-2], profiles[index+1])

        if abs(PD1-PT1) > 0.1 + abs(PD2-PT2):
            return index-1, 'h'
        if abs(PD2 - PT2) > 0.1 + abs(PD1 - PT1):
            return index, 'h'

    return -1, 'i'
