"""
Implements the impossible date test on page 6 of http://w3.jcommops.org/FTPRoot/Argo/Doc/argo-quality-control-manual.pdf
"""

import numpy
import calendar

def test(p):
    """
    Runs the quality control check on profile p and returns a numpy array
    of quality control decisions with False where the data value has
    passed the check and True where it failed.
    """

    # Get the year, month, day and time:
    year = p.year()
    month = p.month()
    day = p.day()
    #time = p.time()

    # initialize qc as false:
    qc = numpy.zeros(1, dtype=bool)

    if year < 1997:
        qc[0] = True
    elif month not in range(1,13):
        qc[0] = True
    elif day not in range(1, calendar.monthrange(year, month)[1] + 1):
        qc[0] = True

    return qc