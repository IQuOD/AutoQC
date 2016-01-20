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

def test(p):
    '''Return quality control decisions.
    '''

    # Use the probe type information from the profile and map to the 
    # WOD database they are contained in. 
    probe_type = p.probe_type()
    if probe_type == 1:
        # MBT.
        db = 'MBT'
    elif probe_type == 2:
        # XBT
        db = 'XBT'
    elif probe_type == 3:
    	# DBT
    	db = ''
    elif probe_type == 4:
        # CTD
        db = 'CTD'
    elif probe_type == 5:
        # STD
        db = ''
    elif probe_type == 6:
        # XCTD
        db = ''
    elif probe_type == 7:
        # Bottle/rossette/net
        db = 'OSD'
    elif probe_type == 8:
        # Underway/intake
        db = ''
    elif probe_type == 9:
        # Profiling float
        db = 'PFL'
    elif probe_type == 10:
        # Moored buoy
        db = 'MRB'
    elif probe_type == 11:
        # Drifting buoy
        db = 'DRB'
    elif probe_type == 12:
        # Towed CTD
        db = ''
    elif probe_type == 13:
        # Animal mounted
        db = 'APB'
    elif probe_type == 14:
        # Bucket
        db = 'OSD'
    elif probe_type == 15:
        # Glider
        db = 'GLD'
    elif probe_type == 16:
        # MicroBT
        db = ''
    else:
        db = ''

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



