from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the density inversion QC from the CoTeDe Argo config.'''

    config   = 'argo'
    testname = 'density_inversion'
    
    try:
        qc = get_qc(p, config, testname)
    except:
        qc = numpy.zeros(1, dtype=bool)

    return qc


