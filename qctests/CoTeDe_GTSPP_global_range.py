from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the global range QC from the CoTeDe GTSPP config.'''

    config   = {'TEMP': {'global_range':{ 'minval': -2.0, 'maxval': 40}}}
    testname = 'global_range'

    return get_qc(p, config, testname)


