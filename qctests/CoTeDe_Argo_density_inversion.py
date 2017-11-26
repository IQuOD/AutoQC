from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the density inversion QC from the CoTeDe Argo config.'''

    config   = 'argo'
    testname = 'density_inversion'
    
    qc = get_qc(p, config, testname)

    return qc


