from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the rate_of_change QC from the CoTeDe config.'''

    config   = 'cotede'
    testname = 'rate_of_change'

    try:
        qc = get_qc(p, config, testname)
    except:
        qc = numpy.zeros(1, dtype=bool)

    return qc

