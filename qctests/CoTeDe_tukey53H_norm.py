from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the tukey53H norm QC from the CoTeDe config.'''

    config   = {'TEMP': {'tukey53H_norm': {'k': 1.5, 'l': 12}}}
    testname = 'tukey53H_norm'

    return get_qc(p, config, testname)


