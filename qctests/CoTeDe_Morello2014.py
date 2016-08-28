from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the CoTeDe Morello 2014 QC.'''

    config   = 'morello2014'
    testname = 'morello2014'
   
    try:
        qc = get_qc(p, config, testname)
    except:
        qc = numpy.zeros(1, dtype=bool)

    return qc


