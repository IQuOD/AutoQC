from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the digit roll over QC from the CoTeDe config.'''

    config   = {'TEMP': {'digit_roll_over': 10}}
    testname = 'digit_roll_over'

    return get_qc(p, config, testname)


