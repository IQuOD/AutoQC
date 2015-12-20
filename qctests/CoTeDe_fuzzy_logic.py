from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the CoTeDe fuzzy logic QC.'''

    config   = 'fuzzy'
    testname = 'fuzzylogic'

    return get_qc(p, config, testname)


