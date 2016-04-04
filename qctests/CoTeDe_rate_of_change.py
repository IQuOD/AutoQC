from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the rate_of_change QC from the CoTeDe config.'''

    config   = {'TEMP': {'rate_of_change': 4}}
    testname = 'rate_of_change'

    return get_qc(p, config, testname)


