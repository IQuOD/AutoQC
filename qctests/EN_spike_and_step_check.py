""" 
Implements the spike and step check used in the EN quality control 
system, pages 20-21 of http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf

The EN quality control system does not directly reject levels that are marked as 
steps, it marks them as suspect and then they are subjected to an extra test (a  
background check) that can reprieve them. In the future it will be best to 
remove these elements and include them within the background check code. 
"""

import numpy as np
import util.main as main

def test(p, parameters, suspect=False):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    
    By default the test returns definite rejections. If the suspect keyword is
    set to True the test instead returns suspect levels.
    """
    
    return run_qc(p, suspect)

def run_qc(p, suspect):

    # check for pre-registered suspect tabulation, if that's what we want:
    if suspect:
        query = 'SELECT suspect FROM enspikeandstep WHERE uid = ' + str(p.uid()) + ';'
        susp = main.dbinteract(query)
        if len(susp) > 0:
            return main.unpack_row(susp[0])[0]
            
    # Define tolerances used.
    tolD     = np.array([0, 200, 300, 500, 600])
    tolDTrop = np.array([0, 300, 400, 500, 600])
    tolT     = np.array([5.0, 5.0, 2.5, 2.0, 1.5])  

    # Define an array to hold results.
    qc    = np.zeros(p.n_levels(), dtype=bool)

    # Get depth and temperature values from the profile.
    z = p.z()
    t = p.t()

    # Find which levels have data.
    isTemperature = (t.mask==False)
    isDepth = (z.mask==False)
    isData = isTemperature & isDepth

    # Array to hold temperature differences between levels and gradients.
    dt, gt = composeDT(t, z, p.n_levels())
        
    # Spikes and steps detection.
    for i in range(1, p.n_levels()):
        if i >= 2:
            if (isData[i-2] and isData[i-1] and isData[i]) == False:
                continue
            if z[i] - z[i-2] >= 5.0:
                wt1 = (z[i-1] - z[i-2]) / (z[i] - z[i-2])
            else:
                wt1 = 0.5
        else:
            if (isData[i-1] and isData[i]) == False:
                continue
            wt1 = 0.5
        
        dTTol = determineDepthTolerance(z[i-1], np.abs(p.latitude()))
        gTTol = 0.05

        # Check for low temperatures in the Tropics.
        # This might be more appropriate to appear in a separate EN regional
        # range check but is included here for now for consistency with the
        # original code.
        if (np.abs(p.latitude()) < 20.0 and z[i-1] < 1000.0 and
            t[i-1] < 1.0):
               dt[i] = np.ma.masked 
               if suspect == True: qc[i-1] = True
               continue
               
        qc, dt = conditionA(dt, dTTol, qc, wt1, i, suspect)                
        qc, dt = conditionB(dt, dTTol, gTTol, qc, gt, i, suspect)
        qc = conditionC(dt, dTTol, z, qc, t, i, suspect)
    
    # End of loop over levels.
    
    # Step or 0.0 at the bottom of a profile.
    if isData[-1] and dt.mask[-1] == False:
        dTTol = determineDepthTolerance(z[-1], np.abs(p.latitude()))
        if np.abs(dt[-1]) > dTTol:
            if suspect == True: qc[-1] = True
    if isTemperature[-1]:
        if t[-1] == 0.0:
            if suspect == True: qc[-1] = True
        
    # If 4 levels or more than half the profile is rejected then reject all.
    if suspect == False:
        nRejects = np.count_nonzero(qc)
        if nRejects >= 4 or nRejects > p.n_levels()/2:
            qc[:] = True

    # register suspects, if computed, to db
    if suspect:
        query = "INSERT INTO enspikeandstep VALUES(?,?);"
        main.dbinteract(query, [p.uid(), main.pack_array(qc)] )

    return qc


def composeDT(var, z, nLevels):
    '''
    build the array of deltas for the variable provided
    '''
    dt = np.ma.zeros(nLevels)
    dt.mask = True
    gt = dt.copy()

    for i in range(1, nLevels):
        if ((z[i] - z[i-1]) <= 50.0 or (z[i] >= 350.0 and (z[i] - z[i-1]) <= 100.0)):
            dt[i] = var[i] - var[i-1]
            gt[i] = dt[i] / np.max([10.0, z[i] - z[i-1]])


    return dt, gt


def determineDepthTolerance(z, lattitude):
    '''
    determine depth tolerance
    '''
    
    if (lattitude < 20.0): 
        depthTol = 300.0
    else:
        depthTol = 200.0

    if z > 600.0:
        tTolFactor = 0.3
    elif z > 500.0:
        tTolFactor = 0.4
    elif z > depthTol + 100.0:
        tTolFactor = 0.5
    elif z > depthTol:
        tTolFactor = 1.0 - 0.005 * (z - depthTol)
    else:
        tTolFactor = 1.0

    return tTolFactor * 5.0

def conditionA(dt, dTTol, qc, wt1, i, suspect):
    '''
    condition A (large spike check)
    '''
    if (dt.mask[i-1] == False and dt.mask[i] == False and np.max(np.abs(dt[i-1:i+1])) > dTTol):
        if np.abs(dt[i] + dt[i-1]) < 0.5*dTTol:
            dt[i-1:i+1] = np.ma.masked
            if suspect == False: qc[i-1] = True
        elif np.abs((1.0-wt1) * dt[i-1] - wt1*dt[i]) < 0.5*dTTol:
            # Likely to be a valid large temperature gradient.
            dt[i-1:i+1] = np.ma.masked # Stops the levels being rechecked.

    return qc, dt

def conditionB(dt, dTTol, gTTol, qc, gt, i, suspect):
    '''
    condition B (small spike check)
    '''
    if (dt.mask[i-1] == False and dt.mask[i] == False and
        np.max(np.abs(dt[i-1:i+1])) > 0.5*dTTol and
        np.max(np.abs(gt[i-1:i+1])) > gTTol and
        np.abs(dt[i] + dt[i-1]) < 0.25*np.abs(dt[i] - dt[i-1])):
        dt[i-1:i+1] = np.ma.masked
        if suspect == False: qc[i-1] = True

    return qc, dt

def conditionC(dt, dTTol, z, qc, t, i, suspect):
    '''
    condition C (steps)
    '''

    if dt.mask[i-1] == False and np.abs(dt[i-1]) > dTTol:
        if z[i-1] <= 250.0 and dt[i-1] < -dTTol and dt[i-1] > -3.0*dTTol:
            # May be sharp thermocline, do not reject.
            pass
        elif i>1 and z[i] - z[i-2] > 0 and np.abs(t[i-1] - interpolate(z[i-1], z[i-2], z[i], t[i-2], t[i])) < 0.5*dTTol:
            # consistent interpolation, do not reject
            pass
        else:
            # mark both sides of the step
            if suspect == True: qc[i-2:i] = True

    return qc

def interpolate(depth, shallow, deep, shallowVal, deepVal):
    '''
    interpolate values at <depth>
    '''

    return (depth - shallow) / (deep - shallow) * (deepVal - shallowVal) + shallowVal 

def loadParameters(parameterStore):

    main.dbinteract("DROP TABLE IF EXISTS enspikeandstep")
    main.dbinteract("CREATE TABLE IF NOT EXISTS enspikeandstep (uid INTEGER, suspect BLOB)")
