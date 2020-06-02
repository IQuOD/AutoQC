'''
Python version of check_aqc_02_crude_range.f. Details of the 
original code are:

c/ DATE:       JANUARY 19 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)

c/ TITLE:      check_aqc_02_crude_range

c/ PURPOSE:
c    to check weather the temperature value is within the crude range
'''

from . import ICDC_aqc_01_level_order as ICDC
import numpy as np

def test(p, parameters):
    '''Return a set of QC decisions. 
    '''
    
    nlevels, z, t = ICDC.reordered_data(p, parameters)

    qc = (t < parminover) | (t > parmaxover)

    for i, tval in enumerate(t):
        if qc[i]: continue # Already rejected.
    
        zval = z[i]

        if np.any((tval >= tcrude1) & (tval <= tcrude2) & 
                  (zval <= zcrude1) & (zval >= zcrude2)):
            qc[i] = True 

    return ICDC.revert_qc_order(p, qc, parameters)

# Ranges:
tcrude1 = np.array(
     [-3.5,-2.5,-2.3,-2.0,-1.4,-1.0,-0.8,-0.5,-0.4,3.0,
      5.0,5.5,6.0,7.0,7.5,8.8,9.5,10.0,11.0,12.0,12.8,13.5,
      14.75,15.0,16.0,17.5,18.5,19.0,20.0,21.4,22.4,23.0,24.0,
      26.0,28.0,31.0,32.0])

tcrude2 = np.array(
     [-2.5,-2.3,-2.0,-1.4,-1.0,-0.8,-0.5,-0.4,3.0,
      5.0,5.5,6.0,7.0,7.5,8.8,9.5,10.0,11.0,12.0,12.8,13.5,
      14.75,15.0,16.0,17.5,18.5,19.0,20.0,21.4,22.4,23.0,24.0,
      26.0,28.0,31.0,32.0,35.0])

zcrude1    = np.ndarray(37)
zcrude1[:] = 9000.0

zcrude2 = np.array(
     [   0., 500.,1200.,2000.,3800.,4200.,
      5000.,6000.,9000.,7500.,4400.,1950.,
      1900.,1800.,1700.,2200.,1700.,5200.,
      1600.,1400.,3600.,5200.,1000., 800.,
      1800., 800., 600., 400., 350.,2400.,
       400., 350., 300., 250., 200., 100., 50.])

parminover = -2.3
parmaxover = 33.0


