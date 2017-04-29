""" 
Implements the EN track check, described on pp 7 and 21 of
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import numpy as np
import util.main as main
import util.geo as geo
import copy, datetime, math, sys, calendar

# module constants
DistRes = 20000. # meters
TimeRes = 600. # seconds

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """
    
    cruise = p.cruise()
    uid = p.uid()
    
    # don't bother if cruise == 0 or None, or if timestamp is corrupt
    if (cruise in [0, None]) or (None in [p.year(), p.month(), p.day(), p.time()]):
        return np.zeros(1, dtype=bool)
    
    # don't bother if this has already been analyzed
    command = 'SELECT en_track_check FROM ' + parameters["table"] + ' WHERE uid = ' + str(uid) + ';'
    en_track_result = main.dbinteract(command)
    if en_track_result[0][0] is not None:
        en_track_result = main.unpack_row(en_track_result[0])[0]
        result = np.zeros(1, dtype=bool)
        result[0] = np.any(en_track_result)
        return result
    
    # some detector types cannot be assessed by this test; do not raise flag.
    if p.probe_type() in [None]:
        return np.zeros(1, dtype=bool)
    
    # fetch all profiles on track, sorted chronologically, earliest first (None sorted as highest)
    command = 'SELECT uid, year, month, day, time, lat, long, probe FROM ' + parameters["table"] + ' WHERE cruise = ' + str(cruise) + ' and year is not null and month is not null and day is not null and time is not null ORDER BY year, month, day, time ASC;'
    track_rows = main.dbinteract(command)

    # start all as passing by default:
    EN_track_results = {}
    for i in range(len(track_rows)):
        EN_track_results[track_rows[i][0]] = np.zeros(1, dtype=bool)
    
    # copy the list of headers;
    # remove entries as they are flagged.
    passed_rows = copy.deepcopy(track_rows)
    rejects = findOutlier(passed_rows, EN_track_results)
    
    while rejects != []:
        passed_index = [x for x in range(len(passed_rows)) if x not in rejects ]
        passed_rows = [passed_rows[index] for index in passed_index ]
        rejects = findOutlier(passed_rows, EN_track_results)
    
    # if more than half got rejected, reject everyone
    if len(passed_rows) < len(track_rows) / 2:
        for i in range(len(track_rows)):
            EN_track_results[track_rows[i][0]][0] = True
   
    # write all to db
    for i in range(len(track_rows)):
        result = main.pack_array(EN_track_results[track_rows[i][0]])
        
        query = "UPDATE " + sys.argv[1] + " SET en_track_check=? WHERE uid = " + str(track_rows[i][0]) + ";"

        main.dbinteract(query, (result,))

    return EN_track_results[uid]

#def sliceTrack(p, rows, margin=7):
#    '''
#    remove all table rows from rows whose dates are more than margin days before or after the month that p falls in
#    each row has row[1] = year, row[2] = month, row[3] = day
#    '''

#    m = datetime.timedelta(days=margin)
#    earliest = datetime.datetime(p.year(), p.month(), 1) - m
#    latest = datetime.datetime(p.year(), p.month(), calendar.monthrange(p.year(), p.month())[1] ) + m

#    inrange = []
#    for row in rows:
#        date = datetime.datetime(row[1], row[2], row[3])
#        if date >= earliest and date <= latest:
#            inrange.append(row)

#    return inrange

def findOutlier(rows, results):
    '''
    given a list of rows, find the fastest one;
    if it's too fast, reject it or the one before it, return a list of rejected indices;
    once the fastest is within limits, return [].
    '''

    maxShipSpeed = 15. # m/s
    maxBuoySpeed = 2. # m/s

    if rows == []:
        return []

    # determine speeds and angles for list of headers
    speeds, angles = calculateTraj(rows)
  
    # decide if something needs to be flagged
    maxSpeed = maxShipSpeed
    if isBuoy(rows[0]):
        maxSpeed = maxBuoySpeed
    iMax = speeds.index(max(speeds))
    flag = detectExcessiveSpeed(speeds, angles, iMax, maxSpeed)

    # decide which profile to reject, flag it, and return a list of indices rejected at this step.
    if flag:
        rejects = chooseReject(rows, speeds, angles, iMax, maxSpeed)
        for reject in rejects:
            results[rows[reject][0]][0] = True
        return rejects
    else:
        return []

def chooseReject(rows, speeds, angles, index, maxSpeed):
    '''
    decide which row to reject, rows[index] or rows[index-1], or both,
    and return a list of indices to reject.
    '''

    # chain of tests breaks when a reject is found:
    reject = condition_a(rows, speeds, angles, index, maxSpeed)[0]

    # condition i needs to run at the end of the chain in all cases:
    # if no decision, reject both:
    if reject == -1:
        reject = [index-1, index]
    # if excessive speed is created by removing the flag, reject both instead 
    # can't create new excessive speed by removing last profile.
    elif reject < len(rows)-1: 
        new_rows = copy.deepcopy(rows)
        del new_rows[reject]
        newSpeeds, newAngles = calculateTraj(new_rows)
        flag = detectExcessiveSpeed(newSpeeds, newAngles, reject, maxSpeed)
        if flag:
            reject = [index-1, index]
        else:
            reject = [reject]
    else:
        reject = [reject]

    return reject

def calculateTraj(rows):
    '''
    return a list of speeds and a list of angles describing the trajectory of the track described
    by the time-ordered list of rows.
    '''

    speeds = [None]
    angles = [None]

    # Find speed and angle for all profiles remaining in the list
    for i in range(1, len(rows)):

        speeds.append(None)
        angles.append(None)
        speeds[i] = trackSpeed(rows[i-1], rows[i])

        if i < len(rows)-1: # can't do angle on last point 
            angles[i] = abs(math.pi - geo.haversineAngle(rows[i-1][5], rows[i-1][6], rows[i][5], rows[i][6], rows[i+1][5], rows[i+1][6]))

    return speeds, angles

def isBuoy(row):
    '''
    decide if row belongs to a buoy-based measurement
    '''
    return row[7] in [4,7,9,10,11,12,13,15]

def detectExcessiveSpeed(speeds, angles, index, maxSpeed):
    '''
    decide if there was an excessive speed at <index> in the lists <speeds> and <angles>
    '''

    flag = speeds[index] > maxSpeed

    if index > 0:
        flag = flag or ( (speeds[index] > 0.8*maxSpeed) and (angles[index]>math.pi/2 or angles[index-1]>math.pi/2) )

    return flag

def meanSpeed(speeds, rows, maxSpeed):
    '''
    determine mean speed, neglecting missing data, intervals less than 1h, and speeds over maxspeed, for use in condition (f)
    '''

    meanSpeed = 0
    speedCount = 0
    for iSpeed, speed in enumerate(speeds):
        if speed == None or iSpeed == 0:
            #missing values
            continue
        elif iSpeed > 0 and geo.deltaTime((rows[iSpeed-1][1], rows[iSpeed-1][2], rows[iSpeed-1][3], rows[iSpeed-1][4]), (rows[iSpeed][1], rows[iSpeed][2], rows[iSpeed][3], rows[iSpeed][4])):
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


def trackSpeed(prev_row, row):
    '''
    computes the speed, including rounding tolerance from the reference,
    for the track at <row>.
    return None if some necessary data is missing
    '''

    # check that all required data (full timestamp + lat + long) is present:
    if None in [row[1], row[2], row[3], row[4], row[5], row[6]]:
        return None
    if None in [prev_row[1], prev_row[2], prev_row[3], prev_row[4], prev_row[5], prev_row[6] ]:
        return None

    dist = geo.haversineDistance(prev_row[5], prev_row[6], row[5], row[6])
    DTime = geo.deltaTime((prev_row[1], prev_row[2], prev_row[3], prev_row[4]), (row[1], row[2], row[3], row[4]))
    speed = (dist - DistRes) / max(DTime, TimeRes)

    return speed

def condition_a(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (a) from the text
    '''

    if index == 1 and len(rows) == 2:
        return 0, 'a'
    elif index == 1 and len(rows) > 2: # note 'M' in the text seems to count from 1, not 0.
        impliedSpeed = trackSpeed(rows[0], rows[2])
        if impliedSpeed < maxSpeed and (speeds[2]>maxSpeed or angles[2]>45./180.*math.pi):
            return 1, 'a'
        else:
            return 0, 'a'
    elif index == len(rows)-1 and len(rows)>3:  # why not >=? seems to cause problems, investigate.
        impliedSpeed = trackSpeed(rows[-3], rows[-1])
        if impliedSpeed < maxSpeed and (speeds[-2] > maxSpeed or angles[-3]>45./180.*math.pi):
            return index-1, 'a'
        else:
            return index, 'a'
    else:
        return condition_b(rows, speeds, angles, index, maxSpeed)

def condition_b(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (b) from the text
    '''

    if speeds[index-1] > maxSpeed:
        return index-1, 'b'
    elif index < len(speeds) - 1 and speeds[index+1] > maxSpeed:
        return index, 'b'

    return condition_c(rows, speeds, angles, index, maxSpeed)

def condition_c(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (c) from the text
    '''

    if index < len(rows)-1 and index > 0:
        impliedSpeed = trackSpeed(rows[index-1], rows[index+1])
        if impliedSpeed > maxSpeed:
            return index-1, 'c'

    if index > 1:
        impliedSpeed = trackSpeed(rows[index-2], rows[index])
        if impliedSpeed > maxSpeed:
            return index, 'c'

    return condition_d(rows, speeds, angles, index, maxSpeed)


def condition_d(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (d) from the text
    '''

    if None not in [angles[index-1], angles[index]] and angles[index-1] > 45./180.*math.pi + angles[index]:
        return index-1, 'd'

    if None not in [angles[index-1], angles[index]] and angles[index] > 45./180.*math.pi + angles[index-1]:
        return index, 'd'

    return condition_e(rows, speeds, angles, index, maxSpeed)

def condition_e(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (e) from the text
    '''

    if len(rows) > max(2, index+1):

        if None not in [angles[index-2], angles[index+1]] and angles[index-2] > 45./180.*math.pi and angles[index-2] > angles[index+1]:
            return index-1, 'e'

        if None not in [angles[index+1]] and angles[index+1] > 45./180.*math.pi:
            return index, 'e'

    return condition_f(rows, speeds, angles, index, maxSpeed)

def condition_f(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (f) from the text
    '''

    if index>0 and index < len(speeds)-1:

        ms = meanSpeed(speeds, rows, maxSpeed)

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index-1] < min([speeds[index+1], 0.5*ms]):
            return index-1, 'f'

        if None not in [speeds[index-1], speeds[index+1]] and speeds[index+1] < min([speeds[index-1], 0.5*ms]):
            return index, 'f'

    return condition_g(rows, speeds, angles, index, maxSpeed)

def condition_g(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (g) from the text
    '''

    if index > 1 and index < len(rows) - 1:
    
        dist1 = geo.haversineDistance(rows[index][5], rows[index][6], rows[index-2][5], rows[index-2][6]) + geo.haversineDistance(rows[index+1][5], rows[index+1][6], rows[index][5], rows[index][6])
        dist2 = geo.haversineDistance(rows[index-1][5], rows[index-1][6], rows[index-2][5], rows[index-2][6]) + geo.haversineDistance(rows[index+1][5], rows[index+1][6], rows[index-1][5], rows[index-1][6])

        distTol = geo.haversineDistance(rows[index-1][5], rows[index-1][6], rows[index-2][5], rows[index-2][6])
        distTol += geo.haversineDistance(rows[index][5], rows[index][6], rows[index-1][5], rows[index-1][6])
        distTol += geo.haversineDistance(rows[index+1][5], rows[index+1][6], rows[index][5], rows[index][6])
        distTol = max(DistRes, 0.1*distTol)

        if dist1 < dist2 - distTol:
            return index-1, 'g'

        if dist2 < dist1 - distTol:
            return index, 'g'

    return condition_h(rows, speeds, angles, index, maxSpeed)

def condition_h(rows, speeds, angles, index, maxSpeed):
    '''
    assess condition (h) from the text
    '''
    
    if index > 1 and index < len(rows) - 1:

        dist1 = geo.haversineDistance(rows[index][5], rows[index][6], rows[index-2][5], rows[index-2][6]) + geo.haversineDistance(rows[index+1][5], rows[index+1][6], rows[index][5], rows[index][6])
        dist2 = geo.haversineDistance(rows[index-1][5], rows[index-1][6], rows[index-2][5], rows[index-2][6]) + geo.haversineDistance(rows[index+1][5], rows[index+1][6], rows[index-1][5], rows[index-1][6])

        PD1 = geo.haversineDistance(rows[index-1][5], rows[index-1][6], rows[index-2][5], rows[index-2][6]) / dist2
        PD2 = geo.haversineDistance(rows[index][5], rows[index][6], rows[index-2][5], rows[index-2][6]) / dist1

        PT1 = geo.deltaTime((rows[index-2][1], rows[index-2][2], rows[index-2][3], rows[index-2][4]), (rows[index-1][1], rows[index-1][2], rows[index-1][3], rows[index-1][4])) / geo.deltaTime((rows[index-2][1], rows[index-2][2], rows[index-2][3], rows[index-2][4]), (rows[index+1][1], rows[index+1][2], rows[index+1][3], rows[index+1][4]))
        PT2 = geo.deltaTime((rows[index-2][1], rows[index-2][2], rows[index-2][3], rows[index-2][4]), (rows[index][1], rows[index][2], rows[index][3], rows[index][4])) / geo.deltaTime((rows[index-2][1], rows[index-2][2], rows[index-2][3], rows[index-2][4]), (rows[index+1][1], rows[index+1][2], rows[index+1][3], rows[index+1][4]))

        if abs(PD1-PT1) > 0.1 + abs(PD2-PT2):
            return index-1, 'h'
        if abs(PD2 - PT2) > 0.1 + abs(PD1 - PT1):
            return index, 'h'

    return -1, 'i'
