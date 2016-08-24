from cotede_qc.cotede_test import get_qc

def test(p, parameters):
    '''Run the global range QC from the CoTeDe GTSPP config.'''

    config   = 'gtspp'
    testname = 'global_range'

    return get_qc(p, config, testname)


