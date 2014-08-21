from dataio import wod
import json
from qctests import EN_range_check

# Read the list of filenames. 
filenames = json.loads(open('datafiles.json').read())

# Read all profiles from the files.
profiles = []
for filename in filenames:
    f = open(filename)
    while True:
        profiles += [wod.WodProfile(f)]
        if profiles[-1].is_last_profile_in_file(f): break
    f.close()

# Placeholder for running the quality control tests using ddt.
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
    print('---------------------------------')


