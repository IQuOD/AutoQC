from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the RoC QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'RoC'

    return get_qc(p, config, testname)


