'''Miscellaneous functions to help with handling WOD data.'''

def wod_database(p):
    '''
    Use the probe type information from the profile and map to the 
    WOD database they are contained in. 

    Input is a wodpy.wod.WodProfile object.

    Returns the three letter database code or UNK for unknown if
    no matching database is identified.
    '''

    probe_type = p.probe_type()
    if probe_type == 1:
        # MBT.
        db = 'MBT'
    elif probe_type == 2:
        # XBT
        db = 'XBT'
    elif probe_type == 3:
    	# DBT
    	db = 'MBT'
    elif probe_type == 4:
        # CTD
        db = 'CTD'
    elif probe_type == 5:
        # STD
        db = 'OSD'
    elif probe_type == 6:
        # XCTD
        db = 'OSD'
    elif probe_type == 7:
        # Bottle/rossette/net
        db = 'OSD'
    elif probe_type == 8:
        # Underway/intake
        db = 'SUR' 
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
        db = 'UOR'
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
        db = 'MBT'
    else:
        db = 'UNK'

    return db

    
