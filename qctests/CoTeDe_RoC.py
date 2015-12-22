from cotede_qc.cotede_test import get_qc

def test(p):
    '''Run the RoC QC from the CoTeDe config.'''

    config   = {'TEMP': {'RoC': 4}}
    testname = 'RoC'

    return get_qc(p, config, testname)


