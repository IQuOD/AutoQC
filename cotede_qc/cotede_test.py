from cotede.qc import ProfileQC
import datetime
import json
import logging
import numpy as np
from wodpy.extra import Wod4CoTeDe

'''Runs QC tests from the CoTeDe package.
   CoTeDe (https://github.com/castelao/CoTeDe) is copyright (c) 2011-2015, Guilherme Pimenta Castelao.
'''

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
    if (p.uid() != cotede_results[0] or 
            config != cotede_results[1] or
                p.uid() is None):
        inputs = Wod4CoTeDe(p)
        if isinstance(config, dict):
            cfg = config
        else:
            with open('cotede_qc/qc_cfg/' + config + '.json') as f:
                cfg = json.load(f)
        cotede_results = [p.uid(), 
                          config, 
                          ProfileQC(inputs, cfg=cfg)]
    
    var = 'TEMP'

    # Get the QC results, which use the IOC conventions.
    qc_returned = cotede_results[2].flags[var][test]

    # It looks like CoTeDe never returns a QC decision
    # of 2. If it ever does, we need to decide whether 
    # this counts as a pass or reject.
    # Gui: Yes, some tests can return 2. My suggestions is to flag as good.
    qc = np.ma.zeros(p.n_levels(), dtype=bool)
    qc[np.logical_or(qc_returned == 3, qc_returned == 4)] = True

    return qc

