'''
Python version of check_aqc_04_instrument_type_max_obs_depth.f. Details of the 
original code are:

c/ DATE:       JANUARY 20 2016

c/ AUTHOR:     Viktor Gouretski

c/ AUTHOR'S AFFILIATION:   Integrated Climate Data Center, University of Hamburg, Hamburg, Germany

c/ PROJECT:    International Quality Controlled Ocean DataBase (IQuOD)


c/ TITLE:      check_aqc_04_instrument_type_max_obs_depth

c/ PURPOSE:
c    compare observed depths with unstrument type maximum observed depth
'''

import ICDC_aqc_01_level_order as ICDC
import numpy as np
from util.wod import wod_database

def test(p):
    '''Return quality control decisions.
    '''

    # Get WOD database.
    db = wod_database(p)

    # Set maximum allowed depth. If not defined, it is set to the highest 
    # possible float.      
    if db == 'OSD':
        zlast = 9000.0
    elif db == 'CTD':
        zlast = 9000.0
    elif db == 'PFL':
        zlast = 2020.0
    elif db == 'APB':
        zlast = 1200.0
    elif db == 'MBT' and p.primary_header['Country code'] == 'JP':
        zlast = 295.00001
    elif db == 'XBT':
        zlast = 1900.0
    else:
        zlast = np.finfo(dtype=float).max

    # Set QC flags.
    qc = p.z() >= zlast

    return qc



