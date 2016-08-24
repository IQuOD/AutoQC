from cotede_qc.cotede_test import get_qc

def test(p, parameters):
    '''Run the CoTeDe fuzzy logic QC.'''

    config   = 'fuzzylogic'
    testname = 'fuzzylogic'

    return get_qc(p, config, testname)


