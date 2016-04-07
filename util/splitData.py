# utility to split a raw datafile up into n roughly equal parts, keeping all profiles for a given cruise in the same file

import math
from wodpy import wod

filename = '../quota_all.dat'
n = 30

fid = open(filename)
fid.read()
fileSize = fid.tell()
chunkSize = int(math.ceil(fileSize / n)); # final files should be about this big

# identify cruise numbers, profile start and profile end positions for all profiles
markers = []
fid.seek(0)
while True:
    start = fid.tell()
    profile = wod.WodProfile(fid)
    end = fid.tell()
    markers.append( (profile.cruise(), start, end) )
    if profile.is_last_profile_in_file(fid) == True:
        break
# sort by cruise number
markers = sorted(markers, key=lambda x: x[0])

# write subfiles
fileNo = 0
currentCruise = None
target = open('split-' + str(fileNo) + '.dat', 'w')
for i in range(len(markers)):
    lastCruise = currentCruise
    currentCruise = markers[i][0]
    # switch out to the next file when we pass chunksize AND are finished the current cruise
    if target.tell() > chunkSize and currentCruise != lastCruise and None not in [lastCruise, currentCruise]:
        target.close()
        fileNo += 1
        target = open('split-' + str(fileNo) + '.dat', 'w')
    fid.seek(markers[i][1])
    extract = fid.read(markers[i][2]-markers[i][1])
    target.write(extract)

target.close()