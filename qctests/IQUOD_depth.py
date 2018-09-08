import numpy

def test(p, parameters):
    """
    flag any single level surface measurement made by an XBT

    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get depth values (m) from the profile.
    d = p.z()
    # is this an xbt?
    isXBT = p.probe_type() == 2

    # initialize qc as a bunch of falses;
    qc = numpy.zeros(p.n_levels(), dtype=bool)

    # only interested in single level surface XBT measurements:
    if p.n_levels() == 1 and d[0] < 1 and isXBT:
        qc[0] = True

    return qc
