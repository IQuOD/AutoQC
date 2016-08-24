'''Returns the suspect levels found by the EN spike and step check.'''

import EN_spike_and_step_check

def test(p, parameters):

    return EN_spike_and_step_check.test(p, parameters, suspect=True)
