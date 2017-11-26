from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the profile_envelop QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'profile_envelop'

    qc = get_qc(p, config, testname)

    return qc


