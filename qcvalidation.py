import qctests.Argo_global_range_check
import qctests.Argo_gradient_test
import qctests.Argo_impossible_date_test
import qctests.Argo_impossible_location_test
import qctests.Argo_pressure_increasing_test
import qctests.Argo_spike_test
import qctests.EN_constant_value_check
import qctests.EN_range_check
import qctests.EN_spike_and_step_check
import qctests.WOD_gradient_check


import util.testingProfile
import numpy

##### Argo_global_range_check ---------------------------------------------------

def test_Argo_global_range_check_temperature():
    '''
    Make sure AGRC is flagging temperature excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([-2.500000001], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly colder than -2.5 C'

    # -2.5 OK
    p = util.testingProfile.fakeProfile([-2.5], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging -2.5 C'

    # 40 OK
    p = util.testingProfile.fakeProfile([40], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging 40 C'

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([40.0000001], [100]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly warmer than 40 C'        

def test_Argo_global_range_check_pressure():
    '''
    Make sure AGRC is flagging pressure excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([5], [-5.00000001]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag pressure slightly below -5 '

    # -5 OK
    p = util.testingProfile.fakeProfile([5], [-5]) 
    qc = qctests.Argo_global_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging pressure of -5'

##### Argo_gradient_test ---------------------------------------------------

def test_Argo_gradient_test_temperature_shallow():
    '''
    Make sure AGT is flagging postive and negative temperature spikes at shallow depths
    '''

    ###
    # shallow - depth < 500 m
    ###

    # pass a marginal positive spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,11,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold (shallow).'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-7,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold (shallow).' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,11.0001,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold (shallow).'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-7.0001,2], [100,200,300]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold (shallow).'

def test_Argo_gradient_test_temperature_deep():
    '''
    Make sure AGT is flagging postive and negative temperature spikes at deep depths
    '''

    ###
    # deep - depth > 500 m
    ###

    # pass a marginal positive spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,5,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold. (deep)'    

    # pass a marginal negative spike (criteria exactly 9 C):
    p = util.testingProfile.fakeProfile([2,-1,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold. (deep)' 

    # fail a marginal positive spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,5.0001,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (deep)'    

    # fail a marginal negative spike (criteria > 9 C):
    p = util.testingProfile.fakeProfile([2,-1.0001,2], [1000,2000,3000]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold. (deep)'

def test_Argo_gradient_test_temperature_threshold():
    '''
    check AGT temperature behavior exactly at depth threshold (500m)
    '''
    # middle value should fail the deep check but pass the shallow check;
    # at threshold, use deep criteria
    p = util.testingProfile.fakeProfile([2,5.0001,2], [400,500,600]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (threshold)'      

    # as above, but passes just above 500m
    p = util.testingProfile.fakeProfile([2,5.0001,2], [400,499,600]) 
    qc = qctests.Argo_gradient_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a spike using deep criteria when shallow should have been used. (threshold)' 

##### Argo_impossible_date_test -------------------------------------------------------

def test_Argo_impossible_date_test_year():
    '''
    year limit in impossible date test
    '''
    p = util.testingProfile.fakeProfile([0], [0], date=[1996, 1, 1, 0]) 
    qc = qctests.Argo_impossible_date_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'Argo impossible date test must reject everything before 1997.'      

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

##### Argo_impossible_location_test ---------------------------------------------------

def test_Argo_impossible_location_nominal_lat():
    '''
    check for flagging an out-of-range latitude
    '''
    p = util.testingProfile.fakeProfile([0], [0], 91, 0) 
    qc = qctests.Argo_impossible_location_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag latitude outside of range [-90, 90]'

def test_Argo_impossible_location_nominal_long():
    '''
    check for flagging an out-of-range long
    '''
    p = util.testingProfile.fakeProfile([0], [0], 0, 181) 
    qc = qctests.Argo_impossible_location_test.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag long outside of range [-180, 180]'

##### Argo_pressure_increasing_test ---------------------------------------------------

def test_Argo_pressure_increasing_test_constantPressure():
    '''
    API test should flag only the subsequent levels of constant pressure.
    '''

    p = util.testingProfile.fakeProfile([2,2,2], [100,100,100]) 
    qc = qctests.Argo_pressure_increasing_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'must flag only subsequent levels of constant pressure.'    

def test_Argo_pressure_increasing_test_pressureInversion():
    '''
    API test should flag only the subsequent levels of constant pressure.
    '''

    p = util.testingProfile.fakeProfile([2,2,2], [100,200,100]) 
    qc = qctests.Argo_pressure_increasing_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    truth[2] = True
    assert numpy.array_equal(qc, truth), 'must flag all levels corresponding to pressure inversion.' 

##### Argo_spike_test ---------------------------------------------------

def test_Argo_spike_test_temperature_shallow():
    '''
    Make sure AST is flagging postive and negative temperature spikes at shallow depths
    '''

    ###
    # shallow - depth < 500 m
    ###

    # pass a marginal positive spike (criteria exactly 6 C):
    p = util.testingProfile.fakeProfile([5,11,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold (shallow).'    

    # pass a marginal negative spike (criteria exactly 6 C):
    p = util.testingProfile.fakeProfile([5,-1,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold (shallow).' 

    # fail a marginal positive spike (criteria > 6 C):
    p = util.testingProfile.fakeProfile([5,11.0001,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold (shallow).'    

    # fail a marginal negative spike (criteria > 6 C):
    p = util.testingProfile.fakeProfile([5,-1.0001,5], [100,200,300]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold (shallow).'

def test_Argo_spike_test_temperature_deep():
    '''
    Make sure AST is flagging postive and negative temperature spikes at deep depths
    '''

    ###
    # deep - depth > 500 m
    ###

    # pass a marginal positive spike (criteria exactly 2 C):
    p = util.testingProfile.fakeProfile([5,7,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a positive spike exactly at threshold. (deep)'    

    # pass a marginal negative spike (criteria exactly 2 C):
    p = util.testingProfile.fakeProfile([5,3,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging a negative spike exactly at threshold. (deep)' 

    # fail a marginal positive spike (criteria > 2 C):
    p = util.testingProfile.fakeProfile([5,7.0001,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (deep)'    

    # fail a marginal negative spike (criteria > 2 C):
    p = util.testingProfile.fakeProfile([5,2.999,5], [1000,2000,3000]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failing to flag a negative spike just above threshold. (deep)'

def test_Argo_spike_test_temperature_threshold():
    '''
    check AST temperature behavior exactly at depth threshold (500m)
    '''
    # middle value should fail the deep check but pass the shallow check;
    # at threshold, use deep criteria
    p = util.testingProfile.fakeProfile([5,7.0001,5], [400,500,600]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failing to flag a positive spike just above threshold. (threshold)'      

    # as above, but passes just above 500m
    p = util.testingProfile.fakeProfile([5,7.0001,5], [400,499,600]) 
    qc = qctests.Argo_spike_test.test(p)
    truth = numpy.zeros(3, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a spike using deep criteria when shallow should have been used. (threshold)' 

#### EN_constant_value_check -------------------------------------------

def test_EN_constant_value_threshold():
    '''
    check EN_constant_value is flagging 90% and above.
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [100,200,300,400,500,600,700,800,900,1000])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.ones(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failing to flag when exactly 90% of measurements are identical'

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,10,10], [100,200,300,400,500,600,700,800,900,1000])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.zeros(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging when less than 90% of measurements are identical'    

def test_EN_constant_value_spacing():
    '''
    check EN_constant_value is requiring identical values to cover at least 100 m range
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,10], [1,2,3,4,5,6,7,8,9,10])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.zeros(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging identical measurements that do not span 100 m of depth.'

def test_EN_constant_value_missing_depth():
    '''
    Ensures EN_constant_value is not getting thrown by missing depths
    '''

    p = util.testingProfile.fakeProfile([0,0,0,0,0,0,0,0,0,0], [100,200,300,400,500,600,700,800,900,None])
    qc = qctests.EN_constant_value_check.test(p)
    truth = numpy.ones(10, dtype=bool)
    assert numpy.array_equal(qc, truth), 'failing to flag when the deepest depth in a run of constant temperature is missing.'

##### EN_range_check ---------------------------------------------------

def test_EN_range_check_temperature():
    '''
    Make sure EN_range_check is flagging temperature excursions
    '''

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([-4.00000001], [100]) 
    qc = qctests.EN_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly colder than -4 C'

    # -4 OK
    p = util.testingProfile.fakeProfile([-4], [100]) 
    qc = qctests.EN_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging -4 C'

    # 40 OK
    p = util.testingProfile.fakeProfile([40], [100]) 
    qc = qctests.EN_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    assert numpy.array_equal(qc, truth), 'incorrectly flagging 40 C'

    # should fail despite rounding
    p = util.testingProfile.fakeProfile([40.0000001], [100]) 
    qc = qctests.EN_range_check.test(p)
    truth = numpy.zeros(1, dtype=bool)
    truth[0] = True
    assert numpy.array_equal(qc, truth), 'failed to flag temperature slightly warmer than 40 C'

##### EN_spike_and_step_check ----------------------------------------------

def test_EN_spike_and_step_check_tropics_prelim():
    '''
    test preliminary tropical rejection
    '''
    p = util.testingProfile.fakeProfile([0, 0, 0, 0], [0, 10, 20, 30], latitude=0.0)
    qc = qctests.EN_spike_and_step_check.test(p)
    truth = numpy.zeros(4, dtype=bool)
    truth[:] = True
    assert numpy.array_equal(qc, truth), 'failed to flag cold temperatures in the tropics'

def test_EN_spike_and_step_check_composeDT():
    assert True

def test_EN_spike_and_step_check_determineDepthTolerance():
    assert True

def test_EN_spike_and_step_check_conditionA():
    '''
    test independent implementation of condition A (large spikes)
    '''

    p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 20, 30], latitude=20.0)
    dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
    qc = numpy.zeros(4, dtype=bool)
    wt1 = 0  
    for i in range(1,4):
        dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
        qc, dt = qctests.EN_spike_and_step_check.conditionA(dt, dTTol, qc, wt1, i)

    truth = numpy.zeros(4, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'condition A failed to flag a large spike'

def test_EN_spike_and_step_check_spike_A_nominal():
    '''
    test condition A spike check in context
    '''
    p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 20, 30], latitude=20.0)
    qc = qctests.EN_spike_and_step_check.test(p)
    truth = numpy.zeros(4, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failed to flag spike identified by condiion A'

def test_EN_spike_and_step_check_conditionA_small_spike():
    '''
    make sure condition A isn't flagging spikes that are too small for it but big enough for A.
    '''

    p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0)
    dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
    qc = numpy.zeros(4, dtype=bool)
    wt1 = 0
    for i in range(1,4):
        dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
        qc, dt = qctests.EN_spike_and_step_check.conditionA(dt, dTTol, qc, wt1, i)

    truth = numpy.zeros(4, dtype=bool)
    assert numpy.array_equal(qc, truth), 'condition A flagged a spike that should only have been flagged by B.'

def test_EN_spike_and_step_check_spike_A_depth_constraint_shallow():
    '''
    condition A spike *except* measurements too far apart to count as spike (shallow) 
    '''
    p = util.testingProfile.fakeProfile([21, 24, 18, 17], [0, 10, 70, 80], latitude=20.0)
    qc = qctests.EN_spike_and_step_check.test(p)
    truth = numpy.zeros(4, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a type A temperature spike spread out too far in depth (shallow)'

def test_EN_spike_and_step_check_spike_A_depth_constraint_deep():
    '''
    condition A spike *except* measurements too far apart to count as spike (deep). 
    '''
    p = util.testingProfile.fakeProfile([20, 21, 18, 17], [500, 510, 670, 680], latitude=20.0)
    qc = qctests.EN_spike_and_step_check.test(p)
    truth = numpy.zeros(4, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged a type A temperature spike spread out too far in depth (deep)'

def test_EN_spike_and_step_check_conditionB():
    '''
    test independent implementation of condition B (small spikes)
    '''

    p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0)
    dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
    qc = numpy.zeros(4, dtype=bool)
    gTTol = 0.05
    for i in range(1,4):
        dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
        qc, dt = qctests.EN_spike_and_step_check.conditionB(dt, dTTol, gTTol, qc, gt, i)

    truth = numpy.zeros(4, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'condition B failed to flag a small spike'

def test_EN_spike_and_step_check_spike_B_nominal():
    '''
    test condition B spike check in context
    '''
    p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0)
    qc = qctests.EN_spike_and_step_check.test(p)
    truth = numpy.zeros(4, dtype=bool)
    truth[1] = True
    assert numpy.array_equal(qc, truth), 'failed to flag spike identified by condition B'

##### WOD_gradient_check ---------------------------------------------------

def test_WOD_gradient_check_temperature_inversion():
    '''
    validate temperaure inversion behavior
    '''

    # should just barely pass; gradient exactly at threshold
    p = util.testingProfile.fakeProfile([100, 130], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged temperature inversion at threshold'    

    # should just barely fail; gradient slightly over threshold
    p = util.testingProfile.fakeProfile([100, 130.00001], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag slight excess temperature inversion' 

def test_WOD_gradient_check_temperature_gradient():
    '''
    validate temperaure gradient behavior
    '''

    # should just barely pass; gradient exactly at threshold
    p = util.testingProfile.fakeProfile([100, 30], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    assert numpy.array_equal(qc, truth), 'flagged temperature gradient at threshold'    

    # should just barely fail; inversion slightly over threshold
    p = util.testingProfile.fakeProfile([100, 29.9999], [100, 200]) 
    qc = qctests.WOD_gradient_check.test(p)
    truth = numpy.zeros(2, dtype=bool)
    truth[0] = True
    truth[1] = True 
    assert numpy.array_equal(qc, truth), 'failed to flag slight excess temperature gradient' 
