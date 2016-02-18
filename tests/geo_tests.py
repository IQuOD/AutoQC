import util.geo as geo
import util.testingProfile
import math

def test_deltaTime_dateAware():
    '''
    make sure deltaTime is coping with real dates correctly
    '''

    # 2 days on a leap year:
    early = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 28, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2004, 3, 1, 0])

    diff = geo.deltaTime(early, late)
    assert diff == 172800., 'incorrect date difference on leap year'

    # 1 day on not a leap year:
    early = util.testingProfile.fakeProfile([0], [0], date=[2005, 2, 28, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2005, 3, 1, 0])

    diff = geo.deltaTime(early, late)
    assert diff == 86400., 'incorrect date difference on non-leap year'

    # 30 days in June:
    early = util.testingProfile.fakeProfile([0], [0], date=[2004, 6, 30, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2004, 7, 1, 0])

    diff = geo.deltaTime(early, late)
    assert diff == 86400., 'should only be 1 day between June 30 and July 1'

    # 31 days in July:
    early = util.testingProfile.fakeProfile([0], [0], date=[2004, 7, 30, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2004, 8, 1, 0])

    diff = geo.deltaTime(early, late)
    assert diff == 172800., 'should be 2 days between July 30 and August 1'

def test_deltaTime_times():
    '''
    make sure deltaTime is dealing with times correctly
    '''  

    # same day, same time:
    early = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 28, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 28, 0])

    diff = geo.deltaTime(early, late)
    assert diff == 0., 'incorrect time difference for identical dates and times'

    # same day, different time:
    early = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 28, 0])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2004, 2, 28, 1.5])

    diff = geo.deltaTime(early, late)
    assert diff == 5400., 'incorrect time difference for identical dates and different times'


    # earlier time on later day
    early = util.testingProfile.fakeProfile([0], [0], date=[2005, 2, 27, 2])
    late  = util.testingProfile.fakeProfile([0], [0], date=[2005, 2, 28, 1])

    diff = geo.deltaTime(early, late)
    assert diff == 82800., 'incorrect time difference for earlier times but later days'

def test_haversineAngle():
    '''
    check some nominal behavior of great circle intersections.
    '''

    A = util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=10)
    B = util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=20)
    C = util.testingProfile.fakeProfile([0], [0], latitude=0, longitude=30)

    angle = geo.haversineAngle(A,B,C) 
    assert angle - math.pi < 0.000001, 'point on a circle had a non-zero angle between them: %f' % angle

    C = util.testingProfile.fakeProfile([0], [0], latitude=90, longitude=20)
    angle = geo.haversineAngle(A,B,C) 
    assert angle - math.pi/2 < 0.000001, 'orthogonal great circles had an angle of %f between them.' % angle

def test_archaversine_domain():
    '''
    make sure archaversine does something sensible if it ends up with an argument of 1+epislon or -1-epsilon
    '''

    assert geo.arcHaversine(1.00000000000000004) == geo.arcHaversine(1.0), 'archaversine fooled by floating point problems'