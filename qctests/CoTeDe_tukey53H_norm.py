from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the tukey53H norm QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'tukey53H_norm'

    try:
        qc = get_qc(p, config, testname)
    except:
        qc = numpy.zeros(1, dtype=bool)

    return qc

