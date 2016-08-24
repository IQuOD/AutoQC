from cotede_qc.cotede_test import get_qc

def test(p, parameters):
    '''Run the spike QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'spike'

    return get_qc(p, config, testname)


