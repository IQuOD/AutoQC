from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the tukey53H norm QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'tukey53H_norm'

    return get_qc(p, config, testname)


