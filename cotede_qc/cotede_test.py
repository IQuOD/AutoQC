from cotede.qc import ProfileQC
import datetime
import json
import logging
import numpy as np

'''Runs QC tests from the CoTeDe package.
   CoTeDe (https://github.com/castelao/CoTeDe) is copyright (c) 2011-2015, Guilherme Pimenta Castelao.
'''

class DummyCNV(object):
    '''Mimics the CNV object from the Seabird package. 
       Seabird (https://github.com/castelao/seabird) is copyright (c) 2011-2015, Guilherme Pimenta Castelao.
    '''
    def __init__(self, p):
        self.p    = p

        # Data section.
        # These are repeated to allow different names.
        longnames = ['Pressure', 'Temperature', 'Salinity']
        names = ['PRES', 'TEMP', 'PSAL']
        self.data    = []
        for i, data in enumerate([p.z(), p.t(), p.s()]):
            data.attributes = {'id':i,
                               'longname':longnames[i],
                               'name':names[i],
                               'span':[np.min(data), np.max(data)]}
            self.data.append(data)
        self.keylist = names

        # Assign date and location.
        self.attributes = {}
        self.get_datetime()
        self.get_location()

    def keys(self):
        """ Return the available keys in self.data
        """
        return self.keylist

    def __getitem__(self, key):
        """ Return the key array from self.data.
        """
        if key in self.keys():
            return self.data[np.nonzero(np.array(self.keys()) == key)[0][0]]
        else:
            raise KeyError(key + ' is not available in data structure')

    def get_datetime(self):
        year  = self.p.year()
        month = self.p.month()
        day   = self.p.day()
        if day == 0: day = 15
        time  = self.p.time()
        if time is None or time < 0 or time >= 24:
            hours   = 0
            minutes = 0
            seconds = 0
        else:
            hours = int(time)
            minutesf = (time - hours) * 60
            minutes  = int(minutesf)
            seconds  = int((minutesf - minutes) * 60)

        self.attributes['datetime'] = datetime.datetime(year, month, day, hours, minutes, seconds)

    def get_location(self):
        self.attributes['LATITUDE']  = self.p.latitude()
        self.attributes['LONGITUDE'] = self.p.longitude()

def get_qc(p, config, test):
    '''Wrapper for running and returning results of CoTeDe tests.
       Inputs are:
         p is a wodpy profile object.
         config is the suite of tests that test comes from e.g. gtspp.
         test is the specific test to get the results from.
    '''

    global cotede_results

    # Disable logging messages from CoTeDe unless they are more
    # severe than a warning. 
    logging.disable('warn')
    
    # Create a dummy results variable if this is the first call.
    try: 
        cotede_results
    except NameError:
        cotede_results = [-1, '', None]
    
    # Check if we need to perform the quality control.
    if p.uid() != cotede_results[0] or config != cotede_results[1]:
        inputs = DummyCNV(p)
        with open('cotede_qc/qc_cfg/' + config + '.json') as f:
            cotede_results = [p.uid(), 
                              config, 
                              ProfileQC(inputs, cfg=json.load(f))]
    
    # Define where the QC results are found.
    if test == 'location_at_sea':
        var = 'common'
    else:
        var = 'TEMP'

    # Get the QC results, which use the IOC conventions.
    qc_returned = cotede_results[2].flags[var][test]

    # It looks like CoTeDe never returns a QC decision
    # of 2. If it ever does, we need to decide whether 
    # this counts as a pass or reject.
    qc = np.ma.zeros(p.n_levels(), dtype=bool)
    if var == 'common':
        if qc_returned == 3 or qc_returned == 4: qc[:] = True
    else:
        qc[np.logical_or(qc_returned == 3, qc_returned == 4)] = True

    return qc

