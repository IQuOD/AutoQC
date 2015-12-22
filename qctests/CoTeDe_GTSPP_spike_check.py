from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the spike QC from the CoTeDe GTSPP config.'''

    config   = {'TEMP': {'spike': 2.0}}
    testname = 'spike'

    return get_qc(p, config, testname)


