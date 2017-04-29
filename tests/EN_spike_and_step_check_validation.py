import qctests.EN_spike_and_step_check

import util.testingProfile
import numpy
import util.main as main

##### EN_spike_and_step_check ----------------------------------------------
class TestClass():

    parameters = {
        "table": 'unit'
    }

    def setUp(self):
        # this qc test will go looking for the profile in question in the db, needs to find something sensible
        main.faketable('unit')
        main.fakerow('unit')
        # need to re-do this every time to refresh the enspikeandstep table
        qctests.EN_spike_and_step_check.loadParameters(self.parameters)

    def tearDown(self):
        main.dbinteract('DROP TABLE unit;')

    def test_EN_spike_and_step_check_composeDT_nominal(self):
        '''
        check that dts are calculated correctly in a non-pathological case
        '''

        p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 20, 30], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        truth = numpy.ma.array([False, 4., -6., -1.], mask=False)
        assert numpy.array_equal(dt, truth), 'incorrect calculation of delta array'

    def test_EN_spike_and_step_check_composeDT_gap(self):
        '''
        ensures dt is not reported when a gap is too large
        '''

        p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 70, 80], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        truth = numpy.ma.array([False, 4., False, -1.], mask=False)
        assert numpy.array_equal(dt, truth), 'reporting delta when measurements too far separated'

    def test_EN_spike_and_step_check_determineDepthTolerance_tropics(self):
        '''
        check depth tolerance calculations match table B1 in the ref for tropical latitude
        '''

        assert qctests.EN_spike_and_step_check.determineDepthTolerance(299, 0) == 5, 'depthTol in tropics miscalculated in z<300m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(350, 0) == 3.75, 'depthTol in tropics not interpolated correctly between 300 and 400 m'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(450, 0) == 2.5, 'depthTol in tropics miscalculated in 400<z<500m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(550, 0) == 2, 'depthTol in tropics miscalculated in 500<z<600m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(601, 0) == 1.5, 'depthTol in tropics miscalculated below 600m'

    def test_EN_spike_and_step_check_determineDepthTolerance_nontopics(self):
        '''
        check depth tolerance calculations match table B1 in the ref for nontropical latitude
        '''

        assert qctests.EN_spike_and_step_check.determineDepthTolerance(199, 50) == 5, 'depthTol in nontropics miscalculated in z<300m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(250, 50) == 3.75, 'depthTol in nontropics not interpolated correctly between 200 and 300 m'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(350, 50) == 2.5, 'depthTol in nontropics miscalculated in 300<z<400m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(550, 50) == 2, 'depthTol in nontropics miscalculated in 500<z<600m range'
        assert qctests.EN_spike_and_step_check.determineDepthTolerance(601, 50) == 1.5, 'depthTol in nontropics miscalculated below 600m'

    def test_EN_spike_and_step_check_tropics_prelim(self):
        '''
        test preliminary tropical rejection
        '''
        p = util.testingProfile.fakeProfile([0, 0, 0, 0], [0, 10, 20, 30], latitude=0.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters, True)
        truth = numpy.zeros(4, dtype=bool)
        truth[:] = True
        assert numpy.array_equal(qc, truth), 'failed to flag cold temperatures in the tropics'

    def test_EN_spike_and_step_check_conditionA(self):
        '''
        test independent implementation of condition A (large spikes)
        suspect == False since condition A is a hard reject
        '''

        p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 20, 30], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        wt1 = 0  
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc, dt = qctests.EN_spike_and_step_check.conditionA(dt, dTTol, qc, wt1, i, False)

        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        assert numpy.array_equal(qc, truth), 'condition A failed to flag a large spike'

    def test_EN_spike_and_step_check_A_nominal(self):
        '''
        test condition A spike check in context
        '''
        p = util.testingProfile.fakeProfile([20, 24, 18, 17], [0, 10, 20, 30], latitude=20.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters)
        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        assert numpy.array_equal(qc, truth), 'failed to flag spike identified by condiion A'

    def test_EN_spike_and_step_check_conditionA_small_spike(self):
        '''
        make sure condition A isn't flagging spikes that are too small for it but big enough for B.
        suspect == False since condition A is a hard reject
        '''

        p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        wt1 = 0
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc, dt = qctests.EN_spike_and_step_check.conditionA(dt, dTTol, qc, wt1, i, False)

        truth = numpy.zeros(4, dtype=bool)
        assert numpy.array_equal(qc, truth), 'condition A flagged a spike that should only have been flagged by B.'

    def test_EN_spike_and_step_check_spike_A_depth_constraint_shallow(self):
        '''
        condition A spike *except* measurements too far apart to count as spike (shallow) 
        '''
        p = util.testingProfile.fakeProfile([21, 24, 18, 17], [0, 10, 70, 80], latitude=20.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters)
        truth = numpy.zeros(4, dtype=bool)
        assert numpy.array_equal(qc, truth), 'flagged a type A temperature spike spread out too far in depth (shallow)'

    def test_EN_spike_and_step_check_spike_A_depth_constraint_deep(self):
        '''
        condition A spike *except* measurements too far apart to count as spike (deep). 
        '''
        p = util.testingProfile.fakeProfile([20, 21, 18, 17], [500, 510, 670, 680], latitude=20.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters)
        truth = numpy.zeros(4, dtype=bool)
        assert numpy.array_equal(qc, truth), 'flagged a type A temperature spike spread out too far in depth (deep)'

    def test_EN_spike_and_step_check_conditionB(self):
        '''
        test independent implementation of condition B (small spikes)
        suspect == False since condition B is a hard reject
        '''

        p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        gTTol = 0.05
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc, dt = qctests.EN_spike_and_step_check.conditionB(dt, dTTol, gTTol, qc, gt, i, False)

        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        assert numpy.array_equal(qc, truth), 'condition B failed to flag a small spike'

    def test_EN_spike_and_step_check_B_nominal(self):
        '''
        test condition B spike check in context
        '''
        p = util.testingProfile.fakeProfile([22.5, 24, 22.5, 22], [500, 510, 520, 530], latitude=20.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters)
        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        assert numpy.array_equal(qc, truth), 'failed to flag spike identified by condition B'

    def test_EN_spike_and_step_check_conditionC(self):
        '''
        test independent implementation of condition C (steps)
        suspect == True since condition C is a suspected reject
        '''

        p = util.testingProfile.fakeProfile([24, 24, 2, 1], [10, 20, 30, 40], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc = qctests.EN_spike_and_step_check.conditionC(dt, dTTol, p.z(), qc, p.t(), i, True)

        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        truth[2] = True
        assert numpy.array_equal(qc, truth), 'condition C failed to flag a step'

    def test_EN_spike_and_step_check_C_nominal(self):
        '''
        test condition C step check in context
        suspect == True since condition C is a suspected reject
        '''
        p = util.testingProfile.fakeProfile([24, 24, 2, 1], [10, 20, 30, 40], latitude=20.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters, True)
        truth = numpy.zeros(4, dtype=bool)
        truth[1] = True
        truth[2] = True
        assert numpy.array_equal(qc, truth), 'failed to flag a step that should have been caught by condition C'

    def test_EN_spike_and_step_check_conditionC_exception_i(self):
        '''
        make sure condition C is not flagging a step admitted by condition i (interpolation)
        suspect == True since condition C is a suspected reject
        '''

        p = util.testingProfile.fakeProfile([13, 13, 2, -9], [310, 320, 330, 340], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc = qctests.EN_spike_and_step_check.conditionC(dt, dTTol, p.z(), qc, p.t(), i, True)

        truth = numpy.zeros(4, dtype=bool)
        assert numpy.array_equal(qc, truth), 'condition C flagged a step that should have been dismissed by interpolation condition (i)'

    def test_EN_spike_and_step_check_conditionC_exception_ii(self):
        '''
        make sure condition C is not flagging a step admitted by condition ii (sharp thermocline)
        suspect == True since condition C is a suspected reject
        '''

        p = util.testingProfile.fakeProfile([13, 13, 2, 2], [10, 20, 30, 40], latitude=20.0)
        dt, gt = qctests.EN_spike_and_step_check.composeDT(p.t(), p.z(), 4)
        qc = numpy.zeros(4, dtype=bool)
        for i in range(1,4):
            dTTol = qctests.EN_spike_and_step_check.determineDepthTolerance(p.z()[i-1], numpy.abs(p.latitude()))
            qc = qctests.EN_spike_and_step_check.conditionC(dt, dTTol, p.z(), qc, p.t(), i, True)

        truth = numpy.zeros(4, dtype=bool)
        assert numpy.array_equal(qc, truth), 'condition C flagged a step that should have been dismissed by sharp thermocline condition (ii)'

    def test_EN_spike_and_step_check_excpetion_C_iii(self):
        '''
        make sure condition C is not flagging a step admitted by condition iii (last step)
        has to be done in context since this part isn't factored into the helper function for C.
        suspect == True since condition C is a suspected reject
        '''
        p = util.testingProfile.fakeProfile([13, 13, 13, 1], [310, 320, 330, 340], latitude=50.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters, True)
        truth = numpy.zeros(4, dtype=bool)
        truth[3] = True
        assert numpy.array_equal(qc, truth), 'flag only the last temperature when a step is found at the end of the profile'

    def test_EN_spike_and_step_check_trailing_zero(self):
        '''
        make sure trailing 0s are getting flagged as suspect
        '''
        p = util.testingProfile.fakeProfile([0, 0, 0, 0], [10, 20, 30, 40], latitude=50.0, uid=8888)
        qc = qctests.EN_spike_and_step_check.test(p, self.parameters, True)
        truth = numpy.zeros(4, dtype=bool)
        truth[3] = True
        assert numpy.array_equal(qc, truth), 'failed to flag a trailing zero'
