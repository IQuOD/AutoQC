from cotede.qc import ProfileQC
from cotede.utils import load_cfg
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
    logging.disable(logging.WARNING)

    # Create a dummy results variable if this is the first call.
    try:
        cotede_results
    except NameError:
        cotede_results = [-1, '', {}, None]

    var = 'TEMP'

    # Check if we need to perform the quality control.
    if (p.uid() != cotede_results[0] or 
            config != cotede_results[1] or
                test not in cotede_results[2] or
                   p.uid() is None):
        inputs = Wod4CoTeDe(p)

        # Load config from CoTeDe
        cfg = load_cfg(config)

        try:
            if test == config:
                # AutoQC runs only on TEMP, so clean the rest.
                for v in cfg['variables'].keys():
                    if v != 'sea_water_temperature':
                        del(cfg['variables'][v])
            # If is a specific test,
            elif test != config:
                # Load from TEMP,
                try:
                    cfg = {'TEMP': {test: dict(cfg['variables']['sea_water_temperature'][test])}}

                # otherwise load it from main.
                except:
                    # The dummy configuration ensures that the results from
                    # 'main' is copied into the results for var.
                    cfg = {'common': {test: dict(cfg['common'][test])}, var: {'dummy': None}}
        except:
            with open('cotede_qc/qc_cfg/' + config + '.json') as f:
                cfg = json.load(f)

        pqc = ProfileQC(inputs, cfg=cfg)

        cotede_results = [p.uid(), config, pqc.flags[var].keys(), pqc]

    # Get the QC results, which use the IOC conventions.
    # cfg was previously reduced to a single test. By using the overall flag
    # is the same for single test but allow to work with composite criterion
    # such as gtspp at once. Ex. if test = 'gtspp', overall is the combination
    # of all GTSPP tests together.
    qc_returned = cotede_results[3].flags[var]['overall']

    # It looks like CoTeDe never returns a QC decision
    # of 2. If it ever does, we need to decide whether 
    # this counts as a pass or reject.
    # Gui: Yes, some tests can return 2. My suggestions is to flag as good.
    qc = np.ma.zeros(p.n_levels(), dtype=bool)
    qc[np.logical_or(qc_returned == 3, qc_returned == 4)] = True

    return qc

