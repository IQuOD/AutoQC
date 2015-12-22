from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the gradient QC from the CoTeDe GTSPP config.'''

    config   = {'TEMP': {'gradient': 10.0}}
    testname = 'gradient'

    return get_qc(p, config, testname)


