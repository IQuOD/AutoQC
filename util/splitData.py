# utility to split a raw datafile up into n roughly equal parts.

import main
import math
from wodpy import wod

filename = '../../AutoQC_raw/quota/quota_all.dat'
#filename = '../data/quota_subset.dat'
n = 30

headers = main.extractProfiles([filename]);

nPerFile = math.ceil(len(headers) / n)
fid = open(filename)

for fileNo in range(n):
    target = open('split-' + str(fileNo) + '.dat', 'w')
    for i in range(int(nPerFile)):
        start = fid.tell()
        profile = wod.WodProfile(fid)
        end = fid.tell()

        fid.seek(start)
        extract = fid.read(end-start)
        target.write(extract)
        fid.seek(end)
        # test for eof
        if fid.read(1) == '':
            break
        fid.seek(end)
    target.close()
