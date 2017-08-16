from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the CoTeDe Anomaly Detection QC.'''

    config   = 'anomaly_detection'
    testname = 'anomaly_detection'

    try:
        qc = get_qc(p, config, testname)
    except:
        qc = numpy.zeros(1, dtype=bool)

    return qc


