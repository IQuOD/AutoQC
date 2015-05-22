import numpy as np

class fakeProfile:
    '''
    generate a fake simplified profile in order to test 
    implementations of qc-tests.
    '''

    def __init__(self, temperatures, depths, latitude=None):
        self.temperatures = temperatures
        self.depths = depths

        self.primary_header = {}
        self.primary_header['Number of levels'] = len(depths)
        self.primary_header['Latitude'] = latitude
        
    def latitude(self):
        """ Returns the latitude of the profile. """
        assert self.primary_header['Latitude'] is not None, 'Latitude has not been set'
        return self.primary_header['Latitude']

    def t(self):
        """ Returns a numpy masked array of temperatures. """
        return self.var_data(self.temperatures)

    def z(self):
        """ Returns a numpy masked array of depths. """
        return self.var_data(self.depths)

    def n_levels(self):
        """ Returns the number of levels in the profile. """
        return self.primary_header['Number of levels']

    def var_data(self, dat):
        """ Returns the data values for a variable given the variable index. """
        data = np.ma.array(np.zeros(len(dat)), mask=True)

        for i in range(len(dat)):
            data[i] = dat[i]
        return data

