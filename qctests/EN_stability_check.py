""" 
Implements the stability check described on pages 8-9 of
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import math, numpy
import util.main as main

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Check if the QC of this profile was already done and if not
    # run the QC.
    query = 'SELECT en_stability_check FROM ' + parameters["table"] + ' WHERE uid = ' + str(p.uid()) + ';'
    qc_log = main.dbinteract(query)
    qc_log = main.unpack_row(qc_log[0])
    if qc_log[0] is not None:
        return qc_log[0]
        
    return run_qc(p, parameters)

def run_qc(p, parameters):

    # Get temperature, salinity, pressure values from the profile.
    t = p.t()
    s = p.s()
    P = p.p()

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(p.n_levels(), dtype=bool)
    
    # check for gaps in data
    isTemperature = (t.mask==False)
    isSalinity = (s.mask==False)
    isPressure = (P.mask==False)
    isData = isTemperature & isSalinity & isPressure

    # calculate potential temperatures
    T = []
    for i in range(0, p.n_levels()):
        T.append(potentialTemperature(s[i], t[i], P[i]))

    for i in range(2,len(t.data)-1):
        if (isData[i] and isData[i-1] and isData[i-2]) == False:
            continue

        delta_rho_k = mcdougallEOS(s[i], T[i], P[i]) - mcdougallEOS(s[i-1], T[i-1], P[i-1]) 
        if delta_rho_k >= -0.03:
            continue;

        delta_rho_k_prev = mcdougallEOS(s[i-1], T[i-1], P[i-1]) - mcdougallEOS(s[i-2], T[i-2], P[i-2])

        if abs(delta_rho_k_prev + delta_rho_k) < 0.25*abs(delta_rho_k_prev - delta_rho_k):
            qc[i-1] = True
        else:
            if isData[i+1] == False:
                continue

            delta_rho_k_next = mcdougallEOS(s[i+1], T[i+1], P[i+1]) - mcdougallEOS(s[i], T[i], P[i])
            if abs(delta_rho_k + delta_rho_k_next) < 0.25*abs(delta_rho_k - delta_rho_k_next):
                qc[i] = True
            else:
                qc[i-1] = True
                qc[i] = True

    #check bottom of profile
    i = p.n_levels()-1
    if isData[i] and isData[i-1]:
        delta_rho_k = mcdougallEOS(s[i], T[i], P[i]) - mcdougallEOS(s[i-1], T[i-1], P[i-1])
        if delta_rho_k < -0.03:
            qc[i] = True

    #check for critical number of flags, flag all if so:
    if sum(qc) >= max(2, len(t.data)/4.):
        qc = numpy.ones(len(t.data), dtype=bool)

    return qc


def mcdougallEOS(salinity, temperature, pressure):
    '''
    equation of state defined in McDougall et al 2003 (http://journals.ametsoc.org/doi/pdf/10.1175/1520-0426%282003%2920%3C730%3AAACEAF%3E2.0.CO%3B2)
    returns density in kg/m^3
    '''

    p1CF = [
         9.99843699e2,
         7.35212840e0,
        -5.45928211e-2,
         3.98476704e-4,
         2.96938239e0,
        -7.23268813e-3,
         2.12382341e-3,
         1.04004591e-2,
         1.03970529e-7,
         5.18761880e-6,
        -3.24041825e-8,
        -1.23869360e-11
    ]

    p2CF = [
         1.0,
         7.28606739e-3,
        -4.60835542e-5,
         3.68390573e-7,
         1.80809186e-10,
         2.14691708e-3,
        -9.27062484e-6,
        -1.78343643e-10,
         4.76534122e-6,
         1.63410736e-9,
         5.30848875e-6,
        -3.03175128e-16,
        -1.27934137e-17
    ]

    p1 =  p1CF[0]
    p1 += p1CF[1]*temperature
    p1 += p1CF[2]*temperature*temperature
    p1 += p1CF[3]*temperature*temperature*temperature
    p1 += p1CF[4]*salinity
    p1 += p1CF[5]*salinity*temperature
    p1 += p1CF[6]*salinity*salinity
    p1 += p1CF[7]*pressure
    p1 += p1CF[8]*pressure*temperature*temperature
    p1 += p1CF[9]*pressure*salinity
    p1 += p1CF[10]*pressure*pressure
    p1 += p1CF[11]*pressure*pressure*temperature*temperature

    p2 =  p2CF[0]
    p2 += p2CF[1]*temperature
    p2 += p2CF[2]*temperature*temperature
    p2 += p2CF[3]*temperature*temperature*temperature
    p2 += p2CF[4]*temperature*temperature*temperature*temperature
    p2 += p2CF[5]*salinity
    p2 += p2CF[6]*salinity*temperature
    p2 += p2CF[7]*salinity*temperature*temperature*temperature
    p2 += p2CF[8]*math.pow(salinity, 1.5)
    p2 += p2CF[9]*math.pow(salinity, 1.5)*temperature*temperature
    p2 += p2CF[10]*pressure
    p2 += p2CF[11]*pressure*pressure*temperature*temperature*temperature
    p2 += p2CF[12]*pressure*pressure*pressure*temperature

    return p1/p2

def potentialTemperature(S, T, p):
    # approximation for potential temperature given in McDougall et al 2003 (http://journals.ametsoc.org/doi/pdf/10.1175/1520-0426%282003%2920%3C730%3AAACEAF%3E2.0.CO%3B2)
    # S in psu, T in degrees C, p in db
    # note p_r = 0 for these fit values

    coef = [
         0,
         1.067610e-5,
        -1.434297e-6,
        -7.566349e-9,
        -8.535585e-6,
         3.074672e-8,
         1.918639e-8,
         1.788718e-10
    ]

    poly =  coef[1]
    poly += coef[2]*S
    poly += coef[3]*p
    poly += coef[4]*T
    poly += coef[5]*S*T
    poly += coef[6]*T*T
    poly += coef[7]*T*p

    return T + p*poly
