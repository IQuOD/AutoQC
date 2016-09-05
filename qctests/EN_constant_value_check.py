""" 
Implements the constant value check used in the EN quality control 
system, described on page 7 of http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import numpy

def test(p, parameters):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    if p.uid() != uid or p.uid() is None:
        run_qc(p)

    # QC results are stored in the module variable.
    return qc

def run_qc(p):

    global qc, uid

    # Get temperature values from the profile.
    t = p.t()
    d = p.z()

    temperatures = {}
    # initialize qc as a bunch of falses (pass by default)
    qc = numpy.zeros(len(t.data), dtype=bool)

    # check for gaps in data
    isTemperature = (t.mask==False)
    isDepth = (d.mask==False)

    #dictionary counts instances of each temperature value
    for i in range(len(t.data)):
        if isTemperature[i]:
            if t.data[i] in temperatures:
                temperatures[t.data[i]] += 1
            else:
                temperatures[t.data[i]] = 1

    for key in temperatures:

        if float(temperatures[key]) / float(len(t.data)) >= 0.9:
            repeats = numpy.where(t.data == key)[0]
            #drop the entries that don't have a depth associated with them;
            #this triggers the 90% rule regardless of the presence of depth data, but
            #ensures that depths are available to assess the range over which constant temps were observed.
            repeatsWithDepth = []
            for j in range(len(repeats)):
                if isDepth[repeats[j]]:
                    repeatsWithDepth.append(repeats[j])
            first = repeatsWithDepth[0]
            last = repeatsWithDepth[-1]

            if d.data[last] - d.data[first] >= 100:
                qc = numpy.ones(len(t.data), dtype=bool) #note everyhing is flagged by this test.

    uid = p.uid()

    return None

uid = None
qc  = None



