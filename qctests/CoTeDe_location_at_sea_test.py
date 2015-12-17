from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the CoTeDe location at sea QC.'''

    config   = 'cotede'
    testname = 'location_at_sea'
    
    return get_qc(p, config, testname)


