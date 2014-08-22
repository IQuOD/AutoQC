from dataio import wod
import json
import numpy as np
from qctests import EN_range_check

# Read the list of data files. 
filenames = json.loads(open('datafiles.json').read())

# Read all profiles from the files and store in a list.
profiles = []
for filename in filenames:
    with open(filename) as f:
        profiles += [wod.WodProfile(f)]
        while profiles[-1].is_last_profile_in_file(f) == False:
            profiles += [wod.WodProfile(f)]

# Placeholder for a section of code that 
#  - detects all quality control checks in dataio.
#  - uses ddt to run all quality control checks on all profiles.
#  - saves the overall result for each in a numpy array.
for profile in profiles:
    # Run a quality control check on this profile.
    qcResults = EN_range_check.test(profile)

    # Print out a summary of the results.
    print('---------------------------------')
    print('Profile ID: %i' % profile.uid())
    print('')
    print('Depth (m) Temp (degC) Result')
    for iLevel, qc in enumerate(qcResults):
        print('%7.1f    %6.1f     %s' % (profile.z()[iLevel], profile.t()[iLevel], qc))   
    print('      OVERALL RESULT: %s' % np.any(qc))
    print('---------------------------------')


