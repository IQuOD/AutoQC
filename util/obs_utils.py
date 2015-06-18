"""A collection of utilities for handling (mainly subsurface ocean) observations"""

import copy
import numpy as np

def t48tot68(t48):
    """Convert from IPTS-48 to IPTS-68 temperature scales,
       as specified in the CF Standard Name information for
       sea_water_temperature
       http://cfconventions.org/Data/cf-standard-names/27/build/cf-standard-name-table.html

       WARNING - the algorithm needs to be checked as the description was unclear.
       
       temperatures are in degrees C"""

    print('WARNING - the description of this conversion appears wrong and needs to be checked')

    t68 = t48 - 4.4e-6 * t48 * (100 - t48)

    return t68

def t68tot90(t68):
    """Convert from IPTS-68 to ITS-90 temperature scales,
       as specified in the CF Standard Name information for
       sea_water_temperature
       http://cfconventions.org/Data/cf-standard-names/27/build/cf-standard-name-table.html
       
       temperatures are in degrees C"""

    t90 = 0.99976 * t68

    return t90

def pottem(T, S, dStart, dEnd=0.0, pressure=False, lat=0.0):
    """Calculate the temperature of water if it is moved from
       depth dStart to dEnd.

       t: initial temperature of the water.
       s: salinity of the water.
       dStart: depth that the parcel of water starts at.
       dEnd: depth that the parcel of water ends up at.
       pressure: set to true if dStart and dEnd are pressures rather than depths.
       lat: if pressure if False, latitude should also be specified."""

    if pressure:
        P0 = dStart
        P1 = dEnd
    else:
        P0 = depth_to_pressure(dStart, lat)
        P1 = depth_to_pressure(dEnd, lat)

    assert P0 <= 20000 and P1 <= 20000 and P0 >= 0 and P1 >= 0, 'Pressure out of range'

    dpp = 1.0e0

    if P1 >= P0:
        DP = dpp
    else:
        DP = -dpp

    P  = P0
    DS = S - 35e0

    TB = (T-((((-2.1687e-16*T+1.8676e-14)*T-4.6206e-13)*P0 
              + ((2.7759e-12*T-1.1351e-10)*DS+((-5.4481e-14*T  
              + 8.733e-12)*T-6.7795e-10)*T+1.8741e-8))*P0      
              + (-4.2393e-8*T+1.8932e-6)*DS                    
              + ((6.6228e-10*T-6.836e-8)*T+8.5258e-6)*T+3.5803e-5)*DP)

    test = 1

    while test > 0.0:
        TA = (TB+2.0e0*((((-2.1687e-16*T+1.8676e-14)*T-4.6206e-13)*P 
                  + ((2.7759e-12*T-1.1351e-10)*DS+((-5.4481e-14*T 
                  + 8.733e-12)*T-6.7795e-10)*T+1.8741e-8))*P 
                  + (-4.2393e-8*T+1.8932e-6)*DS 
                  + ((6.6228e-10*T-6.836e-8)*T+8.5258e-6)*T+3.5803e-5)*DP)

        P  = P + DP
        TB = T
        T  = TA
        test = (P-P1)*(P-DP-P1)

    POTTEM = ((P1-P+DP)*T+(P-P1)*TB)/DP

    return POTTEM

def _depth_to_pressure_scalar(Z, LAT):
    """Convert a depth to a pressure.

       Based on FNZTOP from the NEMOQC source code.

       z:   the depth for conversion.
       lat: latitude.

       Values have to be scalars."""

    #
    #   CHECK VALUE fnztop = 10302.423165             - CRAY 64-BIT
    #                  = 10302.4231650052           - IEEE 64 BIT
    #   FOR Z=10000M, LAT=30.0
    #

    # Definitions
    PI     = 3.14159265358979323846e0
    RADIAN = PI / 180e0
    G1     = 9.780318e0
    G2     = 9.780318e0 * (5.3024e-3 - 5.9e-6 * 4.0e0)
    G3     = -9.780318e0 * 5.9e-6 * 4.0e0
    S      = 35.0e0
    C1P5   = 1.5e0

    AL     = 1e5 / (9.99842594e2+8.24493e-1*S 
                -5.72466e-3*S**C1P5 + 4.8314e-4*S**2)
    RK     = 1.965221e4 + 5.46746e1*S + 7.944e-2*S**C1P5
    RA     = 3.239908e0 + 2.2838e-3*S + 1.91075e-4*S**C1P5
    RB     = 8.50935e-5 - 9.9348e-7*S
    DD     = np.sqrt(RA*RA-4.0e0*RK*RB)
    C1     = 0.5e0/RB
    C2     = RA/RK
    C3     = RB/RK
    C4     = RA/(2.0e0*RB*DD)
    C5     = 2.0e0*RB/(RA-DD)
    C6     = 2.0e0*RB/(RA+DD)
    C7     = 0.5e0*2.226e-6

    MLOOP=200
    MCONV=5
    EPS=1.0e-1

    PA = np.zeros(MCONV)

    P = Z
    IA=0
    EP=0.0

    for I in range(1, MLOOP + 1):

        X = np.sin(RADIAN*LAT)**2
        GS = (G3*X+G2)*X+G1

        PTEMP = P*1.0e-1

        R1=(AL*(PTEMP-C1*np.log((C3*PTEMP+C2)*PTEMP+1.0e0) + 
             C4*np.log((1.0e0 + C5*PTEMP)/(1.0e0+C6*PTEMP))))

        ZZ = R1/(GS+C7*P)

        # ZERRO ERROR

        if (Z == ZZ): return P

        EE = Z - ZZ
        EA = np.abs(EE)

        # SAVE NEW BEST VALUE
        if (IA == 0 or EA < EP):

            IA = 1
            EP = EA
            PA[IA - 1] = P

        # LOOP FOR LIMIT CYCLE
        elif (EA == EP):

            for J in range(1, IA + 1):
                if (P == PA[J - 1]): return P
    
            if (IA < MCONV):
                IA = IA + 1
                PA[IA - 1] = P
        
        # CORRECT P AND LOOP

        P = P+EE

    assert (EA <= EPS), 'Iteration has not converged'

    P = PA[IA - 1]

    return P
    
def depth_to_pressure(z, lat):
    """Converts depths to pressures.
       
       z:    scalar or numpy array of depth (m).
       lat:  scalar or numpy array of latitude (deg)."""

    assert np.array(lat).size > 0 and np.array(z).size > 0, 'No value provided for z or lat'

    # Rather inelegant way of getting this to work - 
    # TODO : rework this.
    if np.array(lat).size == 1 and np.array(z).size == 1:
        p = _depth_to_pressure_scalar(z, lat)
    elif np.array(lat).size > 1 and np.array(z).size == 1:
        p = np.zeros(len(lat))
        for i, l in enumerate(lat):
            p[i] = _depth_to_pressure_scalar(z, l)
    elif np.array(lat).size == 1 and np.array(z).size > 1:       
        p = np.zeros(len(z))
        for i, d in enumerate(z):
            p[i] = _depth_to_pressure_scalar(d, lat)
    else:
        assert len(lat) == len(z), 'Number of lats does not match the number of depths'
        p = np.zeros(len(z))
        for i, d in enumerate(z):
            p[i] = depth_to_pressure(d, lat[i])

    return p

def pressure_to_depth(p, lat):

    """Function to convert from ocean pressure to depth.  Algorithm is
       taken from Ops_OcnPresToDepth.f90 which forms part of the 
       NEMOQC source code (correct as of revision 2468 of the trunk).

       Inputs:
         p   - Pressure scalar in decibars.
         lat - Latitude in degrees.

       Outputs:
          The depth (in metres) corresponding to the input pressures are returned.

       This routine will work with scalars or numpy arrays.
    """

    # Details of the algorithm from Ops_OcnPresToDepth.f90:
    # ---------
    # depth in meters from pressure in decibars using
    # Saunder's and Fofonoff's method.
    # deep-sea res., 1976,23,109-111.
    # formula refitted for 1980 equation of state

    # checkvalue: depth=9712.653 M for P=10000 decibars,
    # latitude=30 deg

    # above for standard ocean: T=0 deg. celcius;
    # S=35 (PSS-78)

    # gr=gravity variation with latitude: Anon (1970)
    # Bulletin Geodesique

    # Also ...
    #
    # Seawater Applications July 2002

    # Sea-Bird uses the formula in UNESCO Technical Papers in 
    # Marine Science No. 44. This is an empirical formula that 
    # takes compressibility (that is, density) into account. 
    # An ocean water
    # column at 0 deg C (t = 0) and 35 PSU (s = 35) is assumed. 

    # The gravity variation with latitude and pressure is computed as: 

    #    g (m/sec2) = 9.780318 * [ 1.0 + ( 5.2788x10 -3  + 2.36x10 -5  * x) * x ] + 1.092x10 -6  * p 

    #    where 
    #    x = [sin (latitude / 57.29578) ] 2 
    #    p = pressure (decibars) 

    # Then, depth is calculated from pressure: 

    #    depth (meters) = [(((-1.82x10 -15  * p + 2.279x10 -10 ) * p - 2.2512x10 -5  ) * p + 9.72659) * p] / g 

    #    where 
    #    p = pressure (decibars) 
    #    g = gravity (m/sec2) 
    # ---------

    X = np.sin( lat / 57.29578e0 )

    X = X**2

    Gr = 9.780318e0 * ( 1.0e0 + ( 5.2788e-3 + 2.36e-5 * X ) * X ) + 1.092e-6 * p

    Depth = ( ( ( -1.82e-15 * p + 2.279e-10 ) * p - 2.2512e-5 ) * p + 9.72659e0 ) * p

    Depth /= Gr

    return Depth

def density(t, s, l, latitude=None):
    """Calculate the density/densities based on:
           t - potential temperature(s) in degC.
           s - salinity(s) in PSU.
           l - level(s) (either pressure or density) in m or db.
           latitude - only set if l contains depths (can be array or scalar) in deg.
      Code is ported from Ops_OceanRhoEOS25 from NEMOQC,
      which uses a 25 term expression given by McDougall et al (2003; JAOT 20, #5),
      which provides an accurate fit to the Feistel and Hagen (1995) equation of state.
      That code is in turn based on the UM routine in RHO_EOS25 (constants in STATE),
      but with salinity in PSU and density in kg m**-3, as in McDougall.

      Test values from McDougall et al (2005) are:
      t = 25C, s = 35psu, p = 2000 db => rho = 1031.654229 kg/m^2.
          20       20         1000             1017.726743
          12       40         8000             1062.928258

      This function is not properly tested for anything other than basic usage.
    """

    # VALUES NEEDED IN THE CALCULATION.
    # Small constant.
    epsln = 1.E-20   

    # 25 coefficients in the realistic equation of state
    a0  =  9.99843699e+02
    a1  =  7.35212840e+00
    a2  = -5.45928211e-02
    a3  =  3.98476704e-04
    a4  =  2.96938239e+00
    a5  = -7.23268813e-03
    a6  =  2.12382341e-03
    a7  =  1.04004591e-02
    a8  =  1.03970529e-07
    a9  =  5.18761880e-06
    a10 = -3.24041825e-08
    a11 = -1.23869360e-11

    b0  =  1.00000000e+00
    b1  =  7.28606739e-03
    b2  = -4.60835542e-05
    b3  =  3.68390573e-07
    b4  =  1.80809186e-10
    b5  =  2.14691708e-03
    b6  = -9.27062484e-06
    b7  = -1.78343643e-10
    b8  =  4.76534122e-06
    b9  =  1.63410736e-09
    b10 =  5.30848875e-06
    b11 = -3.03175128e-16
    b12 = -1.27934137e-17

    # CONVERT DEPTH TO PRESSURE IF NECESSARY.
    if latitude is not None:    
        p = depth_to_pressure(l, latitude)
    else:
        p = l

    # ERROR CHECKING. Disabled as does not work properly with 
    # masked arrays.
    #assert np.count_nonzero(s <= 0.0) == 0, 'Negative salinity values detected'
    #assert np.count_nonzero(p < 0.0) == 0, 'Negative depths detected' 

    # DENSITY CALCULATION.
    p1   = p
    t1   = t
    s1   = s
    t2   = t1 * t1
    sp5  = np.sqrt(s1)
    p1t1 = p1 * t1

    num = (a0 + t1*(a1 + t1*(a2+a3*t1) )                  
              + s1*(a4 + a5*t1  + a6*s1)                  
              + p1*(a7 + a8*t2 + a9*s1 + p1*(a10+a11*t2)))

    den = (b0 + t1*(b1 + t1*(b2 + t1*(b3 + t1*b4)))          
              + s1*(b5 + t1*(b6 + b7*t2) + sp5*(b8 + b9*t2)) 
              + p1*(b10 + p1t1*(b11*t2 + b12*p1)))

    denr = 1.0/(epsln+den)

    rho = num * denr

    return rho
