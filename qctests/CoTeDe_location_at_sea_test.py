from cotede_qc.cotede_test import get_qc
import numpy

def test(p, parameters):
    '''Run the CoTeDe location at sea QC.'''

    config   = 'cotede'
    testname = 'location_at_sea'
    
    qc = get_qc(p, config, testname)

    return qc

