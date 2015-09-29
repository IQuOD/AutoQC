import qctests.Argo_impossible_date_test

import util.testingProfile
import numpy

##### Argo_impossible_date_test -------------------------------------------------------

def test_Argo_impossible_date_test_year():
    '''
    year limit in impossible date test
    '''
    p = util.testingProfile.fakeProfile([0], [0], date=[1699, 1, 1, 0]) 
    qc = qctests.Argo_impossible_date_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'Argo impossible date test must reject everything before 1700.'      

def test_Argo_impossible_date_test_month():
    '''
    month limit in impossible date test
    '''
    p = util.testingProfile.fakeProfile([0], [0], date=[2001, 0, 1, 0]) 
    qc = qctests.Argo_impossible_date_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'Argo impossible date test should reject month=0 (months counted [1-12])'

def test_Argo_impossible_date_test_day_basic():
    '''
    basic day check in impossible date test
    '''
    p = util.testingProfile.fakeProfile([0], [0], date=[2001, 2, 29, 0]) 
    qc = qctests.Argo_impossible_date_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'Argo impossible date test failing to find correct number of days in month presented'

def test_Argo_impossible_date_test_day_leap_year():
    '''
    make sure impossible date check knows about leap years
    '''
    p = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 29, 0]) 
    qc = qctests.Argo_impossible_date_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'Argo impossible date test not correctly identifying leap years'