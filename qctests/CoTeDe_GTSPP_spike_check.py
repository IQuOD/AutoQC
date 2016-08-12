from cotede_qc.cotede_test import get_qc

def test(p, parameters):
    '''Run the spike QC from the CoTeDe GTSPP config.'''

    config   = 'gtspp'
    testname = 'spike'

    return get_qc(p, config, testname)


