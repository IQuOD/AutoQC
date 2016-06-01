from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the digit roll over QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'digit_roll_over'

    return get_qc(p, config, testname)


