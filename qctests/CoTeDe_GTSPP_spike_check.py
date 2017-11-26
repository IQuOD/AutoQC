from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the spike QC from the CoTeDe GTSPP config.'''

    config   = 'gtspp'
    testname = 'spike'

    qc = get_qc(p, config, testname)

    return qc


