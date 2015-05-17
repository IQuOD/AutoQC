""" 
Implements the constant value check used in the EN quality control 
system, described on page 7 of http://www.metoffice.gov.uk/hadobs/en3/OQCpaper.pdf
"""

import numpy

def test(p):
    """ 
    Runs the quality control check on profile p and returns a numpy array 
    of quality control decisions with False where the data value has 
    passed the check and True where it failed. 
    """

    # Get temperature values from the profile.
    t = p.t()
    d = p.z()

    temperatures = {}
    # initialize qc as a bunch of falses (pass by default)
    qc = numpy.zeros(len(t.data), dtype=bool)

    #dictionary counts instances of each temperature value
    for i in range(len(t.data)):
        if t.data[i] in temperatures:
            temperatures[t.data[i]] += 1
        else:
            temperatures[t.data[i]] = 1

    for key in temperatures:

        if float(temperatures[key]) / float(len(t.data)) >= 0.9:
            repeats = numpy.where(t.data == key)[0]
            first  = repeats[0]
            last = repeats[-1]

            if d.data[last] - d.data[first] >= 100:
                qc = numpy.ones(len(t.data), dtype=bool) #note everyhing is flagged by this test.


    return qc


