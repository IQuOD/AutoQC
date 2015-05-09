import numpy as np

class fakeProfile:
    '''
    generate a fake simplified profile in order to test 
    implementations of qc-tests.
    '''

    def __init__(self, temperatures, depths):
        self.temperatures = temperatures
        self.depths = depths

    def t(self):
        """ Returns a numpy masked array of temperatures. """
        return self.var_data(self.temperatures)

    def z(self):
        """ Returns a numpy masked array of depths. """
        return self.var_data(self.depths)

    def var_data(self, dat):
        """ Returns the data values for a variable given the variable index. """
        data = np.ma.array(np.zeros(len(dat)), mask=True)

        for i in range(len(dat)):
            data[i] = dat[i]
        return data
