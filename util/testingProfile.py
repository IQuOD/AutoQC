from datetime import datetime, timedelta
import numpy as np

class fakeProfile:
    '''
    generate a fake simplified profile in order to test 
    implementations of qc-tests.
    '''

    def __init__(self, temperatures, depths, latitude=None, longitude=None, date=[1999, 12, 31, 0], probe_type=None, salinities=None, pressures=None, uid=None, cruise=None):
        self.temperatures = temperatures
        if salinities is None:
            self.salinities = np.ma.array(temperatures, mask=True)
        else:
            self.salinities = salinities
        self.depths = depths
        if pressures is None:
            self.pressures = np.ma.array(temperatures, mask=True)
        else:
            self.pressures = pressures

        self.primary_header = {}
        self.primary_header['Number of levels'] = len(depths)
        self.primary_header['Latitude'] = latitude
        self.primary_header['Longitude'] = longitude
        self.primary_header['Year'] = date[0]
        self.primary_header['Month'] = date[1]
        self.primary_header['Day'] = date[2]
        self.primary_header['Time'] = date[3]
        self.primary_header['WOD unique cast number'] = uid
        self.primary_header['Cruise number'] = cruise
        
        self.secondary_header = {'entries':[]}
        if probe_type is not None:
            self.secondary_header['entries'].append({'Code':29, 'Value':probe_type})

    def latitude(self):
        """ Returns the latitude of the profile. """
        assert self.primary_header['Latitude'] is not None, 'Latitude has not been set'
        return self.primary_header['Latitude']

    def longitude(self):
        """ Returns the longitude of the profile. """
        assert self.primary_header['Longitude'] is not None, 'Longitude has not been set'
        return self.primary_header['Longitude']

    def uid(self):
        """ Returns the unique identifier of the profile. """
        return self.primary_header['WOD unique cast number']

    def cruise(self):
        """ return the cruise number """
        return self.primary_header['Cruise number']

    def t(self):
        """ Returns a numpy masked array of temperatures. """
        return self.var_data(self.temperatures)

    def s(self):
        """ Returns a numpy masked array of salinities. """
        return self.var_data(self.salinities)

    def p(self):
        """ Returns a numpy masked array of salinities. """
        return self.var_data(self.pressures)

    def z(self):
        """ Returns a numpy masked array of depths. """
        return self.var_data(self.depths)

    def n_levels(self):
        """ Returns the number of levels in the profile. """
        return self.primary_header['Number of levels']

    def year(self):
        """ Returns the year. """
        return self.primary_header['Year']

    def month(self):
        """ Returns the month. """
        return self.primary_header['Month']

    def day(self):
        """ Returns the day. """
        return self.primary_header['Day']

    def time(self):
        """ Returns the time. """
        return self.primary_header['Time']

    def datetime(self):
        day = self.primary_header['Day']
        if day == 0:
            day = 15
        time  = self.primary_header['Time']
        if time is None or time < 0 or time >= 24:
            time = 0

        d = datetime(self.year(), self.month(), day) + \
            timedelta(hours=time)
        return d

    def var_data(self, dat):
        """ Returns the data values for a variable given the variable index. """
        data = np.ma.array(np.zeros(len(dat)), mask=True)

        for i in range(len(dat)):
            if dat[i] is not None:
                data[i] = dat[i]
        return data

    def probe_type(self):
        """ Returns the contents of secondary header 29 if it exists,
            otherwise None. """
        pt = None
        for item in self.secondary_header['entries']:
            if item['Code'] == 29:
                pt = item['Value']
        return pt

    def z_level_qc(self):
        return np.zeros(self.depths.shape).astype('bool')

    def t_qc_mask(self):
        return np.zeros(self.temperatures.shape).astype('bool')

