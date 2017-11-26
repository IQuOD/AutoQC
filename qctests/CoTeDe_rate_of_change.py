from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the rate_of_change QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'rate_of_change'

    qc = get_qc(p, config, testname)

    return qc

