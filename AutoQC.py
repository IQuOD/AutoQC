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
        profiles.append(wod.WodProfile(f))
        while profiles[-1].is_last_profile_in_file(f) == False:
            profiles.append(wod.WodProfile(f))

# In some IQuOD datasets temperature values of 99.9 are special values to 
# signify not to use the data value. These are flagged here so they are not
# sent to the quality control programs for testing.
for profile in profiles:
    index = profile.var_index()
    assert index is not None, 'No temperature data in profile %s' % profile.uid()
    for i in range(profile.n_levels()):
        if profile.profile_data[i]['variables'][index]['Missing']: 
            continue
        if profile.profile_data[i]['variables'][index]['Value'] == 99.9:
            profile.profile_data[i]['variables'][index]['Missing'] = True

# Placeholder for a section of code that 
#  - detects all quality control checks in dataio.
#  - uses ddt to run all quality control checks on all profiles.
#  - saves the overall result for each in a numpy array. The overall result
#      is simply whether any level in the profile was rejected by the 
#      quality control.
# The reference results are the correct results for each level of the
# profile. We want to know how often the overall result for the quality 
# control check matches the overall reference result.
nFailedQC  = 0
nFailedRef = 0
for profile in profiles:
    # Run a quality control check on this profile.
    qcResults = EN_range_check.test(profile)
    
    # Extract the reference result for each level.
    qcRefs    = profile.t_level_qc(originator=True) >= 3

    # Print out a summary of the results.
    print('-----------------------------------------')
    print('Profile ID: %i' % profile.uid())
    print('')
    print('Depth (m) Temp (degC) Result Reference')
    for iLevel, qc in enumerate(qcResults):
        print('%6s      %5s     %5s   %5s' % (profile.z()[iLevel], 
                                profile.t()[iLevel], qc, qcRefs[iLevel]))   
    print('     OVERALL RESULTS: %5s   %5s' % 
                                (np.any(qcResults), np.ma.any(qcRefs)))
    print('-----------------------------------------')

    # Collate some statistics.
    if np.any(qcResults): nFailedQC += 1
    if np.ma.any(qcRefs): nFailedRef += 1

print('Number of profiles tested was %i' % len(profiles))
print('Number of profiles that failed the quality control test was %i' %
                                                                      nFailedQC)
print('Number of profiles that should have been failed was %i' % nFailedRef)


                                                                      

