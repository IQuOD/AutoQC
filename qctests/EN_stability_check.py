""" 
Implements the stability check described on pages 8-9 of
http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import math, numpy

def test(p, **kwargs):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get temperature, salinity, pressure values from the profile.
    t = p.t()
    s = p.s()
    p = p.p()

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isSalinity = (s.mask==False)
    isPressure = (p.mask==False)
    isData = isTemperature & isSalinity & isPressure

    levelFlags = numpy.zeros(len(t.data), dtype=bool)

    for i in range(1,len(t.data)-1):
        pass

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
