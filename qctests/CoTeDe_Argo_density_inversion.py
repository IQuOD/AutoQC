from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the density inversion QC from the CoTeDe Argo config.'''

    config   = 'argo'
    testname = 'density_inversion'

    return get_qc(p, config, testname)


