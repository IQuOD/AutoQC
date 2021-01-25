from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the tukey53H QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'tukey53H'

    qc = get_qc(p, config, testname)

    return qc

