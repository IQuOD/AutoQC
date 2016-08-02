from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the CoTeDe Morello 2014 QC.'''

    config   = 'morello2014'
    testname = 'morello2014'

    return get_qc(p, config, testname)


