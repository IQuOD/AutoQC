from cotede_qc.cotede_test import get_qc

def test(p, parameters):
    '''Run the CoTeDe Anomaly Detection QC.'''

    config   = 'anomaly_detection'
    testname = 'anomaly_detection'

    return get_qc(p, config, testname)


