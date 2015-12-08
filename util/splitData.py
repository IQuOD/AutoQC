# utility to split a raw datafile up into n roughly equal parts.

import main
import math
from wodpy import wod

#filename = '../../AutoQC_raw/quota/quota_all.dat'
#filename = '../data/quota_subset.dat'
filename = '../../AutoQC_raw/quota/test/chunk.dat'
n = 30

fid = open(filename)
fid.read()
fileSize = fid.tell()
chunkSize = int(math.ceil(fileSize / n));

fileNo = 0
start = 0
end = 0

target = open('split-' + str(fileNo) + '.dat', 'w')
fid.seek(0)
while not (fid.read(1) == ''):
    #write next chunk to open target
    fid.seek(end)
    start = fid.tell()
    profile = wod.WodProfile(fid)
    end = fid.tell()
    fid.seek(start)
    extract = fid.read(end-start)
    target.write(extract)

    #wrap the file and start a new one once we've crossed the max size
    if target.tell() > chunkSize:
        target.close()
        fileNo += 1
        target = open('split-' + str(fileNo) + '.dat', 'w')
