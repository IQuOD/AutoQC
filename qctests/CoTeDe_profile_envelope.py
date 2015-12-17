from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the profile_envelope QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'profile_envelope'

    return get_qc(p, config, testname)


