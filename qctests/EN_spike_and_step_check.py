""" 
Implements the spike and step check used in the EN quality control 
system. 

The EN quality control system is actually more complicated than is represented
here. Rather than directly reject levels that are marked as steps, it 
marks them as suspect and then they are subjected to an extra test (a  
background check) that can reprieve them. In the future it will be best to 
remove these elements and include them within the background check code. 
"""

import numpy as np

def test(p, *args, **kwargs):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

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
    dt = np.ma.zeros(p.n_levels())
    dt.mask = True
    gt = dt.copy()
        
    # Spikes and steps detection.
    for i in range(1, p.n_levels()):
        if i >= 2:
            if (isData[i-2] and isData[i-1] and isData[i]) == False:
                continue
            if z[i] - z[i-2] >= 5.0:
                wt1 = (z[i-1] - z[i-2]) / (z[i] - z[i-2])
        else:
            if (isData[i-1] and isData[i]) == False:
                continue
            wt1 = 0.5
        
        # Define tolerance for use later.
        if (np.abs(p.latitude()) < 20.0): 
            depthTol = 300.0
        else:
            depthTol = 200.0
        if z[i-1] > 600.0:
            tTolFactor = 0.3
        elif z[-1] > 500.0:
            tTolFactor = 0.4
        elif z[i-1] > depthTol + 100.0:
            tTolFactor = 0.5
        elif z[i-1] > depthTol:
            tTolFactor = 1.0 - 0.005 * (z[i-1] - depthTol)
        else:
            tTolFactor = 1.0
        dTTol = tTolFactor * 5.0
        gTTol = 0.05

        if ((z[i] - z[i-1]) <= 50.0 or 
            (z[i] >= 350.0 and (z[i] - z[i-1]) <= 100.0)):
            dt[i] = t[i] - t[i-1]
            gt[i] = dt[i] / np.max([10.0, z[i] - z[i-1]])

        # Check for low temperatures in the Tropics.
        # This might be more appropriate to appear in a separate EN regional
        # range check but is included here for now for consistency with the
        # original code.
        if (np.abs(p.latitude()) < 20.0 and z[i-1] < 1000.0 and
            t[i-1] < 1.0):
               dt[i] = np.ma.masked 
               qc[i-1] = True
               continue
               
        # Check for spikes.
        if (dt.mask[i-1] == False and dt.mask[i] == False and
            np.max(np.abs(dt[i-1:i+1])) > dTTol):
            if np.abs(dt[i] + dt[i-1]) < 0.5*dTTol:
                dt[i-1:i+1] = np.ma.masked
                qc[i-1] = True
            elif np.abs((1.0-wt1) * dt[i-1] - wt1*dt[i]) < 0.5*dTTol:
                # Likely to be a valid large temperature gradient.
                dt[i-1:i+1] = np.ma.masked # Stops the levels being rechecked.
                
        # Check for sharp, small amplitude spikes.
        if (dt.mask[i-1] == False and dt.mask[i] == False and
            np.max(np.abs(dt[i-1:i+1])) > 0.5*dTTol and
            np.max(np.abs(gt[i-1:i+1])) > gTTol and
            np.abs(dt[i] + dt[i-1]) < 0.25*np.abs(dt[i] - dt[i-1])):
            dt[i-1:i+1] = np.ma.masked
            qc[i-1] = True
        
        # Check for steps.
        if dt.mask[i-1] == False and np.abs(dt[i-1]) > dTTol:
            if z[i-1] <= 250.0 and dt[i-1] < -dTTol and dt[i-1] > -3.0*dTTol:
                # May be sharp thermocline, do not reject.
                pass
            else:
                qc[i-2:i] = True
    
    # End of loop over levels.
    
    # Step or 0.0 at the bottom of a profile.
    if dt.mask[-1] and np.abs(dt[-1]) > dTTol:
        qc[-1] = True
    if t[-1] == 0.0:
        qc[-1] = True
        
    # If 4 levels or more than half the profile is rejected then reject all.
    nRejects = np.count_nonzero(qc)
    if nRejects >= 4 or nRejects > p.n_levels()/2:
        qc[:] = True

    return qc


